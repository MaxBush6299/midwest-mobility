"""Engineering / PLM fixture-backed tools (Gate B Task 13)."""
from __future__ import annotations
from pathlib import Path

from agent_framework import tool
from mmc_agents.tools.fixtures_loader import _read, load_fixture

_FIX = Path(__file__).resolve().parents[3] / "enterprise" / "engineering-plm" / "fixtures"


@tool(description="Look up the PLM part master row for a part.")
def part_master(part_id: str) -> dict:
    return load_fixture(_FIX / "plm_part_master.json", part_id) or {
        "status": "not_found",
        "part_id": part_id,
    }


@tool(description="Return ECO rows for a part.")
def eco_status(part_id: str) -> list[dict]:
    return _read(str(_FIX / "eco_log.json")).get(part_id, [])


@tool(description="Return effectivity rows for a part, optionally filtered by plant.")
def effectivity(part_id: str, plant_id: str | None = None) -> list[dict]:
    rows = _read(str(_FIX / "effectivity.json")).get(part_id, [])
    if plant_id is None:
        return rows
    return [r for r in rows if r["Plant_ID"] == plant_id]
