"""Tests for the governance metadata loader + blast-radius computation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mmc_agents.governance.blast_radius import (
    BlastRadius,
    compute_all_blast_radii,
    compute_blast_radius,
)
from mmc_agents.governance.metadata import (
    InfraMetadata,
    KbMetadata,
    load_infra_metadata,
    load_kb_metadata,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]


def test_governance_metadata_loads_cleanly() -> None:
    """Both JSON files must validate against the Pydantic schema."""
    kb = load_kb_metadata()
    infra = load_infra_metadata()
    assert isinstance(kb, KbMetadata)
    assert isinstance(infra, InfraMetadata)
    assert len(kb.knowledge_bases) == 3
    assert {k.id for k in kb.knowledge_bases} == {"kb-plant7", "kb-plant4", "kb-enterprise"}


def test_every_agent_in_kb_metadata_has_a_foundry_project() -> None:
    kb = load_kb_metadata()
    infra = load_infra_metadata()
    for agent in kb.per_agent_readable_sources:
        assert infra.project_for_agent(agent) is not None, (
            f"agent {agent!r} is in kb_metadata but not assigned to any foundry_project"
        )


def test_every_per_agent_source_exists_in_its_kb() -> None:
    kb = load_kb_metadata()
    for agent, mapping in kb.per_agent_readable_sources.items():
        kb_obj = kb.kb(mapping.kb)
        known = {s.id for s in kb_obj.sources}
        unknown = set(mapping.sources) - known
        assert not unknown, (
            f"agent {agent!r} references unknown sources {sorted(unknown)} in KB {mapping.kb}"
        )


def test_search_service_kbs_match_kb_metadata() -> None:
    kb = load_kb_metadata()
    infra = load_infra_metadata()
    kb_ids = {k.id for k in kb.knowledge_bases}
    for svc in infra.search_services:
        assert svc.kb in kb_ids, f"search service {svc.name} points at unknown KB {svc.kb}"


def test_blast_radius_for_sql_agent_includes_full_chain() -> None:
    """Plant 7 training touches a SQL source -> must surface SQL server + table + Contributor role."""
    kb = load_kb_metadata()
    infra = load_infra_metadata()
    br = compute_blast_radius("plant7-training", kb, infra)
    assert isinstance(br, BlastRadius)
    assert br.foundry_project == "mmc-plant"
    assert br.knowledge_base == "kb-plant7"
    kinds = {e.kind for e in br.edges}
    # must include the full grounding chain
    assert {
        "foundry_project",
        "knowledge_base",
        "kb_source",
        "search_service",
        "sql_server",
        "sql_table",
        "model_deployment",
    } <= kinds
    # Search MI Contributor on SQL server is on the path because training_data is SQL
    sql_role = [
        e for e in br.edges
        if e.kind == "search_identity_role" and "Contributor" in e.target
    ]
    assert sql_role, "Contributor role on SQL server missing for SQL-backed agent"


def test_blast_radius_for_docs_only_agent_omits_sql_chain() -> None:
    """Engineering/PLM is documents-only -> SQL server edges and the Contributor SQL role
    must NOT appear on its overlay (they aren't on this agent's path)."""
    kb = load_kb_metadata()
    infra = load_infra_metadata()
    br = compute_blast_radius("ent-engineering-plm", kb, infra)
    kinds = {e.kind for e in br.edges}
    assert "sql_server" not in kinds
    assert "sql_table" not in kinds
    sql_role = [
        e for e in br.edges
        if e.kind == "search_identity_role" and "Contributor" in e.target and "sql-mmc-demo" in e.target
    ]
    assert not sql_role, "Contributor role on SQL server leaked onto a docs-only agent"


def test_blast_radius_unknown_agent_raises() -> None:
    kb = load_kb_metadata()
    infra = load_infra_metadata()
    with pytest.raises(KeyError):
        compute_blast_radius("plant7-nonsense", kb, infra)


def test_compute_all_blast_radii_covers_full_catalog() -> None:
    kb = load_kb_metadata()
    infra = load_infra_metadata()
    radii = compute_all_blast_radii(kb, infra)
    assert set(radii) == set(kb.per_agent_readable_sources)
    assert len(radii) == 16
    assert "plant7-external-auditor" in radii
    assert {f"plant4-{r}" for r in ("ehs", "maintenance", "quality", "shiftops", "training")} <= set(radii)


def test_external_auditor_blast_radius_omits_restricted_source():
    """Sensitivity-demo invariant: the auditor's overlay must NOT include
    `ehs_restricted` or `incident_data` — those are exactly the sources the
    audience expects the auditor to be denied."""
    kb = load_kb_metadata()
    infra = load_infra_metadata()
    br = compute_blast_radius("plant7-external-auditor", kb, infra)
    source_targets = {e.target for e in br.edges if e.kind == "kb_source"}
    assert source_targets == {"ehs"}
    assert "ehs_restricted" not in source_targets
    assert "incident_data" not in source_targets


def test_generated_blast_radius_json_matches_current_metadata() -> None:
    """The checked-in snapshot must match what the generator would produce now —
    catches the 'I edited the YAML but forgot to re-run the generator' bug."""
    kb = load_kb_metadata()
    infra = load_infra_metadata()
    fresh = {
        name: br.model_dump()
        for name, br in compute_all_blast_radii(kb, infra).items()
    }
    snapshot_path = _REPO_ROOT / "governance" / "blast_radius.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert snapshot["agents"] == fresh, (
        "governance/blast_radius.json is stale — re-run "
        "`.venv\\Scripts\\python.exe scripts\\generate_blast_radius.py`."
    )
