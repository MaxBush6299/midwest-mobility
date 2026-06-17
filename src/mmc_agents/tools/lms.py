"""Plant 7 LMS fixture-backed stub (Gate B Task 19)."""
from __future__ import annotations
from pathlib import Path

from agent_framework import tool
from mmc_agents.tools.fixtures_loader import _read, load_fixture

_FIX = Path(__file__).resolve().parents[3] / "plants" / "plant7" / "fixtures" / "lms.json"


@tool(description="Return employees with a Completed training record matching a course query.")
def qualified_employees(course_query: str) -> list[dict]:
    rows = _read(str(_FIX)).values()
    q = course_query.lower()
    return [
        r for r in rows
        if r.get("Status") == "Completed"
        and (q in r.get("Course_Code", "").lower() or q in r.get("Course_Title", "").lower())
    ]


@tool(description="Look up the most recent training record for an employee.")
def training_status(employee_id: str) -> dict:
    for row in _read(str(_FIX)).values():
        if row.get("Employee_ID") == employee_id:
            return row
    return {"status": "not_found", "employee_id": employee_id}
