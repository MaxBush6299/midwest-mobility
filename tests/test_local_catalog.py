# tests/test_local_catalog.py
import json
from pathlib import Path
from mmc_agents.registry.local_catalog import LocalCatalogSource, WatchedLocalCatalogSource

CARD = {
    "name": "x-agent",
    "display_name": "X",
    "description": "demo",
    "endpoint": "https://example/.well-known/agent-card.json",
    "skills": [{"id": "do_x", "description": "do X"}],
    "tier": "plant",
}

def write_catalog(p: Path, cards):
    p.write_text(json.dumps({"agents": cards}))

def test_local_catalog_reads_file(tmp_path: Path):
    cat = tmp_path / "catalog.json"
    write_catalog(cat, [CARD])
    src = LocalCatalogSource(cat)
    agents = src.list_agents()
    assert len(agents) == 1
    assert agents[0].name == "x-agent"

def test_watched_picks_up_new_card(tmp_path: Path):
    cat = tmp_path / "catalog.json"
    write_catalog(cat, [CARD])
    src = WatchedLocalCatalogSource(cat)
    assert len(src.list_agents()) == 1
    second = {**CARD, "name": "y-agent"}
    write_catalog(cat, [CARD, second])
    assert {a.name for a in src.list_agents()} == {"x-agent", "y-agent"}


def test_governance_catalog_includes_external_auditor_for_sensitivity_demo():
    """plant7-external-auditor must be present + have ONLY [ehs] in its readable
    sources — that is the sensitivity-demo invariant. If a future profile edit
    accidentally hands the auditor `ehs_restricted` or `incident_data`, this
    fails loudly and the demo's whole point would be silently broken."""
    agents = LocalCatalogSource(Path("agents/catalog.json")).list_agents()
    names = {a.name for a in agents}
    assert "plant7-external-auditor" in names

    import json
    kb_meta = json.loads(Path("governance/kb_metadata.json").read_text(encoding="utf-8"))
    auditor = kb_meta["per_agent_readable_sources"]["plant7-external-auditor"]
    assert auditor["sources"] == ["ehs"], (
        "External auditor must NOT have access to ehs_restricted or incident_data "
        "— the sensitivity-demo overlay depends on this invariant"
    )


def test_gate_b_catalog_has_all_16_agents_after_refresh():
    """After scripts/refresh_catalog.py runs (Gate D world), the catalog must
    contain 6 plant7 + 5 plant4 + 5 enterprise agents."""
    agents = LocalCatalogSource(Path("agents/catalog.json")).list_agents()
    names = {a.name for a in agents}
    assert len(names) == 16, names
    assert {
        "plant7-ehs", "plant7-external-auditor", "plant7-maintenance",
        "plant7-quality", "plant7-shiftops", "plant7-training",
        "plant4-ehs", "plant4-maintenance", "plant4-quality",
        "plant4-shiftops", "plant4-training",
        "ent-supply-chain", "ent-procurement", "ent-engineering-plm",
        "ent-quality", "ent-demand-program",
    } == names
