"""Catalog contract test for the multi-plant Gate D world.

Locks in the expected agent roster after Plant 4 onboarding and the
Plant 7 external-auditor backfill:

- 5 enterprise agents (ent-* tier)
- 6 plant7 agents (5 core + external-auditor)
- 5 plant4 agents (no external-auditor by design — sensitivity-demo
  is a Plant 7-only role per plants/plant7/profile.yaml comments)

If the catalog grows (new plant, new shared role), update this test
deliberately rather than ignoring the mismatch.
"""
from __future__ import annotations

import json
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent / "agents" / "catalog.json"

EXPECTED_PLANT7 = {
    "plant7-ehs",
    "plant7-maintenance",
    "plant7-quality",
    "plant7-shiftops",
    "plant7-training",
    "plant7-external-auditor",
}

EXPECTED_PLANT4 = {
    "plant4-ehs",
    "plant4-maintenance",
    "plant4-quality",
    "plant4-shiftops",
    "plant4-training",
}

EXPECTED_ENTERPRISE_PREFIX = "ent-"


def _load() -> list[dict]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))["agents"]


def test_catalog_has_expected_total_agents() -> None:
    agents = _load()
    names = [a["name"] for a in agents]
    assert len(names) == len(set(names)), f"duplicate names: {names}"
    assert len(agents) == 16, f"expected 16 agents, got {len(agents)}: {sorted(names)}"


def test_catalog_contains_all_plant7_agents() -> None:
    agents = _load()
    names = {a["name"] for a in agents if a.get("metadata", {}).get("plant_id") == "plant7"}
    assert names == EXPECTED_PLANT7, f"plant7 mismatch: missing={EXPECTED_PLANT7 - names}, extra={names - EXPECTED_PLANT7}"


def test_catalog_contains_all_plant4_agents() -> None:
    agents = _load()
    names = {a["name"] for a in agents if a.get("metadata", {}).get("plant_id") == "plant4"}
    assert names == EXPECTED_PLANT4, f"plant4 mismatch: missing={EXPECTED_PLANT4 - names}, extra={names - EXPECTED_PLANT4}"


def test_catalog_contains_enterprise_agents() -> None:
    agents = _load()
    ent_names = [a["name"] for a in agents if a["name"].startswith(EXPECTED_ENTERPRISE_PREFIX)]
    assert len(ent_names) == 5, f"expected 5 enterprise agents (ent-*), got {len(ent_names)}: {sorted(ent_names)}"


def test_plant4_cards_point_at_plant4_project() -> None:
    agents = _load()
    plant4 = [a for a in agents if a.get("metadata", {}).get("plant_id") == "plant4"]
    assert plant4, "no plant4 agents in catalog"
    for a in plant4:
        # endpoint should reference the per-plant Foundry project for plant4.
        assert "mmc-plant4" in a["endpoint"], (
            f"{a['name']} endpoint does not target mmc-plant4 project: {a['endpoint']}"
        )
        assert a["metadata"].get("project") == "mmc-plant4"
