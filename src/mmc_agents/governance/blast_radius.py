"""Blast-radius computation for the governance overlay.

The *blast radius* of an agent is the closed set of identities, roles, and
resources that, if revoked or removed, would silently break that agent's
ability to answer. The trace UI overlays this onto each agent card so a
viewer can answer "what would I have to revoke to make this agent stop
working?" without leaving the screen.

For the MMC demo, an agent depends on:

1. Its Foundry project (where the agent lives).
2. The KB attached to that project.
3. The *specific* KB sources it is allowed to retrieve from
   (``per_agent_readable_sources`` in ``kb_metadata.json``).
4. The Search service that physically backs that KB.
5. The role assignments held by that Search service's managed identity that
   make the KB->LLM grounding leg work.
6. For any SQL-backed source, the Azure SQL server + table the indexer pulls
   from, and the Search MI's role on that server.
7. The Foundry model deployments the agent calls (worker + manager).

This module is deliberately *pure* — no Azure calls, no environment reads —
so it can power the UI overlay, the generator script, and unit tests with
the same code path.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from mmc_agents.governance.metadata import (
    AgentName,
    InfraMetadata,
    KbMetadata,
    RoleAssignment,
)

EdgeKind = Literal[
    "foundry_project",
    "knowledge_base",
    "kb_source",
    "search_service",
    "search_identity_role",
    "sql_server",
    "sql_table",
    "model_deployment",
]


class BlastRadiusEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: EdgeKind
    target: str
    detail: str
    revocation_effect: str = Field(
        description=(
            "Plain-English statement of what stops working if the target is "
            "revoked, deleted, or its permission removed. Powers the demo "
            "'revoke this and watch it break' moment."
        )
    )


class BlastRadius(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent: AgentName
    foundry_project: str
    knowledge_base: str | None
    summary: str
    edges: list[BlastRadiusEdge]


def compute_blast_radius(
    agent: AgentName,
    kb_meta: KbMetadata,
    infra_meta: InfraMetadata,
) -> BlastRadius:
    """Build the full blast-radius graph for one agent.

    Raises ``KeyError`` if the agent is not present in either metadata file
    so a typo in the catalog can't silently produce an empty overlay.
    """
    project = infra_meta.project_for_agent(agent)
    if project is None:
        raise KeyError(
            f"agent {agent!r} is not assigned to any foundry_project in infra_metadata.json"
        )

    readable = kb_meta.agent_readable(agent)
    kb_id = readable.kb if readable else project.kb
    kb = kb_meta.kb(kb_id)
    search = infra_meta.search_service_for_kb(kb_id)

    edges: list[BlastRadiusEdge] = []

    edges.append(
        BlastRadiusEdge(
            kind="foundry_project",
            target=project.name,
            detail=f"Agent {agent} is deployed in Foundry project {project.name}.",
            revocation_effect=(
                f"If project {project.name} is deleted or the agent is removed "
                "from it, the agent endpoint goes away entirely."
            ),
        )
    )

    edges.append(
        BlastRadiusEdge(
            kind="knowledge_base",
            target=kb.id,
            detail=f"KB {kb.id} ({kb.display_name}) is attached to project {project.name}.",
            revocation_effect=(
                f"If the KB connection on project {project.name} is deleted, "
                "the agent loses all retrieval grounding and answers from the "
                "base model only."
            ),
        )
    )

    source_ids = readable.sources if readable else []
    for sid in source_ids:
        try:
            src = kb.source(sid)
        except KeyError:
            edges.append(
                BlastRadiusEdge(
                    kind="kb_source",
                    target=sid,
                    detail=f"DRIFT: source {sid} is mapped to agent but not present in KB {kb.id}.",
                    revocation_effect="Already broken — fix governance metadata.",
                )
            )
            continue
        if src.kind == "sql_table":
            edges.append(
                BlastRadiusEdge(
                    kind="kb_source",
                    target=src.id,
                    detail=(
                        f"SQL source {src.id} -> table {src.sql_table}. "
                        f"{src.description}"
                    ),
                    revocation_effect=(
                        f"If source {src.id} is removed from KB {kb.id} or the "
                        f"indexer is paused, the agent loses row-level access "
                        f"to {src.sql_table} and can only answer from procedure docs."
                    ),
                )
            )
            edges.append(
                BlastRadiusEdge(
                    kind="sql_table",
                    target=str(src.sql_table),
                    detail=(
                        f"Backing table on {infra_meta.sql_server.name}/"
                        f"{infra_meta.sql_server.database}."
                    ),
                    revocation_effect=(
                        "Dropping or renaming this table breaks the next "
                        "change-tracking pull; existing index rows stay until refresh."
                    ),
                )
            )
        else:
            edges.append(
                BlastRadiusEdge(
                    kind="kb_source",
                    target=src.id,
                    detail=(
                        f"Document source {src.id}. {src.description} "
                        f"Paths: {', '.join(src.paths or [])}."
                    ),
                    revocation_effect=(
                        f"If source {src.id} is removed from KB {kb.id}, the "
                        f"agent loses retrieval grounding for those documents."
                    ),
                )
            )

    if search is not None:
        edges.append(
            BlastRadiusEdge(
                kind="search_service",
                target=search.name,
                detail=(
                    f"Azure AI Search {search.name} physically hosts the "
                    f"indexes for KB {kb.id}. Identity: {search.managed_identity}."
                ),
                revocation_effect=(
                    "Deleting the search service or its system-assigned identity "
                    "breaks every KB query for every agent on this KB."
                ),
            )
        )
        sql_tables_in_play = {
            kb.source(sid).sql_table
            for sid in source_ids
            if sid in {s.id for s in kb.sources}
            and kb.source(sid).kind == "sql_table"
        }
        for ra in search.role_assignments:
            if (
                ra.role == "Contributor"
                and ra.scope == infra_meta.sql_server.name
                and not sql_tables_in_play
            ):
                # Don't surface the SQL-server contributor role for agents
                # whose sources are all documents — it isn't on their path.
                continue
            edges.append(
                BlastRadiusEdge(
                    kind="search_identity_role",
                    target=f"{ra.principal} :: {ra.role} @ {ra.scope}",
                    detail=ra.purpose,
                    revocation_effect=_role_revocation_effect(ra, kb.id, agent),
                )
            )

        if any(
            kb.source(sid).kind == "sql_table"
            for sid in source_ids
            if sid in {s.id for s in kb.sources}
        ):
            edges.append(
                BlastRadiusEdge(
                    kind="sql_server",
                    target=infra_meta.sql_server.name,
                    detail=(
                        f"Azure SQL {infra_meta.sql_server.name}/"
                        f"{infra_meta.sql_server.database}; auth: {infra_meta.sql_server.auth_mode}."
                    ),
                    revocation_effect=(
                        "Stopping the server, dropping the database, or revoking "
                        "the Search MI's Entra access breaks the next indexer pull."
                    ),
                )
            )

    for dep in infra_meta.foundry_account.model_deployments:
        edges.append(
            BlastRadiusEdge(
                kind="model_deployment",
                target=dep.name_env,
                detail=dep.purpose,
                revocation_effect=(
                    f"Deleting the {dep.name_env} deployment or exhausting its "
                    "quota stalls runs at the next call to that model."
                ),
            )
        )

    summary_parts = [
        f"Agent **{agent}** lives in Foundry project **{project.name}** and "
        f"is grounded by KB **{kb.id}** ({len(source_ids)} source(s) readable)."
    ]
    if any(
        kb.source(sid).kind == "sql_table"
        for sid in source_ids
        if sid in {s.id for s in kb.sources}
    ):
        summary_parts.append(
            f"SQL grounding flows through {search.name if search else '?'} -> "
            f"{infra_meta.sql_server.name}/{infra_meta.sql_server.database}."
        )

    return BlastRadius(
        agent=agent,
        foundry_project=project.name,
        knowledge_base=kb.id,
        summary=" ".join(summary_parts),
        edges=edges,
    )


def _role_revocation_effect(ra: RoleAssignment, kb_id: str, agent: AgentName) -> str:
    if ra.role == "Cognitive Services User":
        return (
            f"Revoke this and the Search MI can no longer call Foundry models, "
            f"so KB {kb_id} stops grounding any answer — agent {agent} included."
        )
    if ra.role == "Azure AI Project User":
        return (
            "Revoke this and the Search MI can no longer publish KB hits back "
            "into the Foundry project's grounding pipeline."
        )
    if ra.role == "Contributor":
        return (
            "Revoke this on the SQL server scope and the IndexedSqlKnowledgeSource "
            "can no longer resolve the server endpoint — next change-tracking pull fails."
        )
    return f"Removing {ra.role} at {ra.scope} disables the {ra.purpose.lower()}"


def compute_all_blast_radii(
    kb_meta: KbMetadata,
    infra_meta: InfraMetadata,
) -> dict[AgentName, BlastRadius]:
    """Build the blast-radius graph for every agent in ``per_agent_readable_sources``."""
    return {
        agent: compute_blast_radius(agent, kb_meta, infra_meta)
        for agent in kb_meta.per_agent_readable_sources
    }
