# tests/test_supplier_tool.py
from mmc_agents.tools.supplier import lookup, alternates

def test_lookup_acme():
    s = lookup("SUP-001")
    assert s is not None
    assert s["Supplier_Name"] == "Acme Brakes"
    assert s["Disruption_Flag"] == "Y"
    assert int(s["Disruption_Days"]) == 21

def test_lookup_unknown():
    assert lookup("SUP-999") == {"status": "not_found", "supplier_id": "SUP-999"}

def test_alternates_returns_no_direct_alt_for_brake_caliper():
    """Gate B Task 27 — BRK-CAL-XYZ is the demo NO_DIRECT_ALT trigger so the
    Magentic manager must backtrack to procurement/PLM/demand."""
    alts = alternates("BRK-CAL-XYZ")
    assert isinstance(alts, list) and len(alts) == 1
    assert alts[0]["status"] == "NO_DIRECT_ALT"
    assert alts[0]["incumbent_supplier_id"] == "SUP-001"


def test_alternates_returns_other_suppliers_when_part_has_approved_alts():
    alts = alternates("STM-PNL-A1")
    assert isinstance(alts, list)
    assert all(a.get("status") != "NO_DIRECT_ALT" for a in alts)
    assert all(a["Supplier_ID"] != "SUP-002" for a in alts)
