"""Tests for src/mmc_agents/tools/procurement.py (Gate B Task 12)."""
from mmc_agents.tools.procurement import contract_terms, po_impact, should_cost


def test_contract_terms_for_acme_brake_part():
    result = contract_terms("SUP-001", "BRK-CAL-XYZ")
    assert result["Contract_ID"] == "CON-0001"
    assert result["Expedite_Allowed"] == "Y"


def test_po_impact_returns_at_risk_pos_for_part():
    rows = po_impact("BRK-CAL-XYZ")
    assert rows and any(r["Status"] == "At Risk" for r in rows)


def test_should_cost_known_part():
    result = should_cost("BRK-CAL-XYZ")
    assert float(result["Current_Unit_Price"]) >= float(result["Should_Cost"])


def test_unknown_contract_returns_not_found():
    assert contract_terms("SUP-999", "NOPE") == {
        "status": "not_found",
        "supplier_id": "SUP-999",
        "part_id": "NOPE",
    }
