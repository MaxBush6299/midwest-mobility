"""Typed loaders for the governance metadata JSON files.

The JSON in ``governance/`` is hand-curated (and audited at code-review time)
rather than generated from live ARM state — it captures the *logical* topology
the demo relies on so a viewer can reason about it without Azure access. These
Pydantic models exist to (1) fail loudly if the JSON drifts from the schema
the rest of the governance code assumes, and (2) provide ergonomic accessors
for the blast-radius computation in :mod:`mmc_agents.governance.blast_radius`.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[3]
_GOVERNANCE_DIR = _REPO_ROOT / "governance"

KbId = str  # ``kb-plant7`` | ``kb-enterprise`` (kept open for future plants)
SourceId = str
AgentName = str
SourceKind = Literal["documents", "sql_table"]


class KnowledgeSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: SourceId
    kind: SourceKind
    description: str
    paths: list[str] | None = None
    sql_table: str | None = None


class KnowledgeBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: KbId
    display_name: str
    foundry_project: str
    search_service: str
    sources: list[KnowledgeSource]

    def source(self, source_id: SourceId) -> KnowledgeSource:
        for s in self.sources:
            if s.id == source_id:
                return s
        raise KeyError(f"source {source_id!r} not found in KB {self.id!r}")


class AgentReadableSources(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kb: KbId
    sources: list[SourceId]


class KbMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    description: str
    knowledge_bases: list[KnowledgeBase]
    per_agent_readable_sources: dict[AgentName, AgentReadableSources]

    def kb(self, kb_id: KbId) -> KnowledgeBase:
        for k in self.knowledge_bases:
            if k.id == kb_id:
                return k
        raise KeyError(f"knowledge base {kb_id!r} not found")

    def agent_readable(self, agent: AgentName) -> AgentReadableSources | None:
        return self.per_agent_readable_sources.get(agent)


class RoleAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principal: str
    role: str
    scope: str
    purpose: str


class SearchService(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    kb: KbId
    managed_identity: str
    role_assignments: list[RoleAssignment]


class ModelDeployment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name_env: str
    purpose: str


class FoundryAccount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    endpoint_env: str
    model_deployments: list[ModelDeployment]


class FoundryProject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    kb: KbId
    search_service: str
    agents: list[AgentName]


class IndexedTable(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table: str
    owner_source: SourceId
    owner_kb: KbId


class SqlServer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    database: str
    auth_mode: str
    indexed_tables: list[IndexedTable]


class InfraMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    description: str
    foundry_account: FoundryAccount
    foundry_projects: list[FoundryProject]
    search_services: list[SearchService]
    sql_server: SqlServer

    def project_for_agent(self, agent: AgentName) -> FoundryProject | None:
        for p in self.foundry_projects:
            if agent in p.agents:
                return p
        return None

    def search_service_for_kb(self, kb_id: KbId) -> SearchService | None:
        for s in self.search_services:
            if s.kb == kb_id:
                return s
        return None


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"governance metadata file not found: {path} — did you run from the repo root?"
        )
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_kb_metadata(path: Path | None = None) -> KbMetadata:
    """Load + validate ``governance/kb_metadata.json`` (cached)."""
    target = path or _GOVERNANCE_DIR / "kb_metadata.json"
    return KbMetadata.model_validate(_read_json(target))


@lru_cache(maxsize=1)
def load_infra_metadata(path: Path | None = None) -> InfraMetadata:
    """Load + validate ``governance/infra_metadata.json`` (cached)."""
    target = path or _GOVERNANCE_DIR / "infra_metadata.json"
    return InfraMetadata.model_validate(_read_json(target))
