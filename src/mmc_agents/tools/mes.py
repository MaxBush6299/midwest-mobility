"""Plant 7 MES fixture-backed stub (Gate B Task 19)."""
from __future__ import annotations
from pathlib import Path

from agent_framework import tool
from mmc_agents.tools.fixtures_loader import _read

_FIX = Path(__file__).resolve().parents[3] / "plants" / "plant7" / "fixtures" / "mes.json"


@tool(description="Return MES line schedule rows for a Plant 7 line.")
def line_schedule(line_id: str) -> list[dict]:
    return [r for r in _read(str(_FIX)).values() if r.get("Line_ID") == line_id]
