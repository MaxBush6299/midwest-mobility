"""Warranty / recall fixture-backed tools (Gate B Task 14)."""
from __future__ import annotations
from pathlib import Path

from agent_framework import tool
from mmc_agents.tools.fixtures_loader import _read

_FIX = Path(__file__).resolve().parents[3] / "enterprise" / "enterprise-quality" / "fixtures"


@tool(description="Return warranty claims for a part.")
def warranty_claims(part_id: str) -> list[dict]:
    return _read(str(_FIX / "warranty_claims.json")).get(part_id, [])


@tool(description="Return field failure rows for a part.")
def field_failures(part_id: str) -> list[dict]:
    return _read(str(_FIX / "field_failure_feed.json")).get(part_id, [])


@tool(description="Return recall thresholds for a part family (e.g., 'Brake').")
def recall_thresholds(part_family: str) -> list[dict]:
    rules = _read(str(_FIX / "recall_ruleset.json"))
    return [r for r in rules.values() if r["Part_Family"].lower() == part_family.lower()]
