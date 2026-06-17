"""Plant 7 QMS / NCR fixture-backed tool (Gate B Task 18)."""
from __future__ import annotations
from pathlib import Path

from agent_framework import tool
from mmc_agents.tools.fixtures_loader import _read, load_fixture

_FIX = Path(__file__).resolve().parents[3] / "plants" / "plant7" / "fixtures" / "qms.json"


@tool(description="Look up Plant 7 NCR status by NCR ID.")
def ncr_status(ncr_id: str) -> dict:
    return load_fixture(_FIX, ncr_id) or {"status": "not_found", "ncr_id": ncr_id}


@tool(description="Return quality signal rows for a part.")
def quality_signals_for_part(part_id: str) -> list[dict]:
    return [r for r in _read(str(_FIX)).values() if r.get("Part_ID") == part_id]
