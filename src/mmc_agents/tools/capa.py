"""Plant 7 CAPA fixture-backed tool (Gate B Task 17)."""
from __future__ import annotations
from pathlib import Path

from agent_framework import tool
from mmc_agents.tools.fixtures_loader import _read, load_fixture

_FIX = Path(__file__).resolve().parents[3] / "plants" / "plant7" / "fixtures" / "capa.json"


@tool(description="Look up Plant 7 CAPA by CAPA ID.")
def capa_status(capa_id: str) -> dict:
    return load_fixture(_FIX, capa_id) or {"status": "not_found", "capa_id": capa_id}


@tool(description="Look up Plant 7 CAPA by originating incident ID.")
def capa_by_incident(incident_id: str) -> dict:
    for row in _read(str(_FIX)).values():
        if row.get("Incident_ID") == incident_id:
            return row
    return {"status": "not_found", "incident_id": incident_id}
