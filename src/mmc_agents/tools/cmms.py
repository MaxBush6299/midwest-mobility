"""Plant 7 CMMS fixture-backed tool (Gate B Task 18)."""
from __future__ import annotations
from pathlib import Path

from agent_framework import tool
from mmc_agents.tools.fixtures_loader import _read

_FIX = Path(__file__).resolve().parents[3] / "plants" / "plant7" / "fixtures" / "cmms.json"


@tool(description="Return PM status rows for a Plant 7 asset.")
def pm_status(asset_id: str) -> list[dict]:
    return [r for r in _read(str(_FIX)).values() if r.get("Asset_ID") == asset_id]


@tool(description="Return PM/maintenance history for an asset.")
def asset_history(asset_id: str) -> list[dict]:
    return pm_status(asset_id)
