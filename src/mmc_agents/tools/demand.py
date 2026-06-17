"""Demand / allocation fixture-backed tools (Gate B Task 15)."""
from __future__ import annotations
from pathlib import Path

from agent_framework import tool
from mmc_agents.tools.fixtures_loader import _read

_FIX = Path(__file__).resolve().parents[3] / "enterprise" / "demand-program" / "fixtures"


@tool(description="Return OEM order signals for a part.")
def order_signal(part_id: str) -> list[dict]:
    return _read(str(_FIX / "order_crm_feed.json")).get(part_id, [])


@tool(description="Return program plan rows for a program code.")
def program_status(program_code: str) -> list[dict]:
    return _read(str(_FIX / "program_plan.json")).get(program_code, [])


@tool(description="Return allocation rows for a part, optionally filtered by plant.")
def allocation(part_id: str, plant_id: str | None = None) -> list[dict]:
    rows = _read(str(_FIX / "allocation_model.json")).get(part_id, [])
    if plant_id is None:
        return rows
    return [r for r in rows if r["Plant_ID"] == plant_id]
