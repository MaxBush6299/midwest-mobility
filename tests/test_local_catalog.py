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
