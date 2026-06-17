"""Tests for src/mmc_agents/tools/plm.py (Gate B Task 13)."""
from mmc_agents.tools.plm import part_master, eco_status, effectivity


def test_part_master_brake_caliper():
    assert part_master("BRK-CAL-XYZ")["Revision"] == "C"


def test_eco_status_for_part():
    rows = eco_status("BRK-CAL-XYZ")
    assert rows and rows[0]["ECO_ID"] == "ECO-2026-014"


def test_effectivity_for_part_and_plant():
    rows = effectivity("BRK-CAL-XYZ", "plant7")
    assert rows and rows[0]["Line_ID"] == "L1"


def test_unknown_part_master():
    assert part_master("NOPE") == {"status": "not_found", "part_id": "NOPE"}
