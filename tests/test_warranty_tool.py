"""Tests for src/mmc_agents/tools/warranty.py (Gate B Task 14)."""
from mmc_agents.tools.warranty import warranty_claims, field_failures, recall_thresholds


def test_warranty_claims_for_brake_caliper():
    assert len(warranty_claims("BRK-CAL-XYZ")) >= 5


def test_field_failures_include_potential_safety():
    assert any(r["Potential_Safety"] == "Y" for r in field_failures("BRK-CAL-XYZ"))


def test_recall_thresholds_for_brake_family():
    assert any(r["Action"] == "Open safety review" for r in recall_thresholds("Brake"))


def test_warranty_claims_unknown_part_returns_empty():
    assert warranty_claims("NOPE") == []
