# src/mmc_agents/tools/erp.py
from __future__ import annotations
from pathlib import Path
from mmc_agents.tools.fixtures_loader import load_fixture

# Agent Framework's @tool decorator. Verify exact import on Microsoft Learn.
from agent_framework import tool  # TODO(verify): exact module path

_FIX = Path(__file__).resolve().parents[3] / "enterprise" / "supply-chain" / "fixtures" / "bom_where_used.json"

@tool(description="Look up where a part is used: returns supplier, plant, line, qty.")
def bom_where_used(part_id: str) -> dict:
    hit = load_fixture(_FIX, part_id)
    if hit is None:
        return {"status": "not_found", "part_id": part_id}
    return hit
