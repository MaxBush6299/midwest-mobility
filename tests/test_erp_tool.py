# tests/test_erp_tool.py
from mmc_agents.tools.erp import bom_where_used

def test_bom_where_used_finds_known_part():
    result = bom_where_used("BRK-CAL-XYZ")
    assert result is not None
    assert result["Plant_ID"] == "plant7"
    assert result["Line_ID"] == "L1"
    assert result["Supplier_ID"] == "SUP-001"

def test_bom_where_used_unknown_part_returns_not_found():
    result = bom_where_used("DOES-NOT-EXIST")
    assert result == {"status": "not_found", "part_id": "DOES-NOT-EXIST"}
