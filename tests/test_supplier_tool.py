# tests/test_supplier_tool.py
from mmc_agents.tools.supplier import lookup, alternates

def test_lookup_acme():
    s = lookup("SUP-001")
    assert s is not None
    assert s["Name"] == "Acme Brakes"
    assert s["Disruption_Flag"] == "Y"
    assert int(s["Disruption_Days"]) == 21

def test_lookup_unknown():
    assert lookup("SUP-999") == {"status": "not_found", "supplier_id": "SUP-999"}

def test_alternates_returns_other_supplier_when_part_known():
    # For the thin slice, alternates is keyed by part_id; returns ALL other suppliers
    # of parts at the same plant/line as a deterministic placeholder.
    alts = alternates("BRK-CAL-XYZ")
    assert isinstance(alts, list)
    assert all(a["Supplier_ID"] != "SUP-001" for a in alts)
