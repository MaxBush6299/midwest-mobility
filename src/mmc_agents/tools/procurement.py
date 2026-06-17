"""Procurement fixture-backed tools (Gate B Task 12)."""
from __future__ import annotations
from pathlib import Path

from agent_framework import tool
from mmc_agents.tools.fixtures_loader import _read, load_fixture

_FIX = Path(__file__).resolve().parents[3] / "enterprise" / "procurement" / "fixtures"


@tool(description="Look up contract terms for a supplier-part pair.")
def contract_terms(supplier_id: str, part_id: str) -> dict:
    contracts_by_part = _read(str(_FIX / "contracts.json"))
    for row in contracts_by_part.get(part_id, []):
        if row["Supplier_ID"] == supplier_id:
            return row
    return {"status": "not_found", "supplier_id": supplier_id, "part_id": part_id}


@tool(description="Return open purchase-order impact for a part.")
def po_impact(part_id: str) -> list[dict]:
    return _read(str(_FIX / "po.json")).get(part_id, [])


@tool(description="Return should-cost model for a part.")
def should_cost(part_id: str) -> dict:
    return load_fixture(_FIX / "should_cost_model.json", part_id) or {
        "status": "not_found",
        "part_id": part_id,
    }
