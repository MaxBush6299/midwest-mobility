"""Live smoke test for the brake-caliper Magentic scenario (Task 28).

Skipped unless MMC_LIVE=1. Requires deployed Foundry project + KBs + agents.
"""
from __future__ import annotations

import asyncio
import os

import pytest
from dotenv import load_dotenv

load_dotenv()

LIVE = os.environ.get("MMC_LIVE", "0") == "1"

pytestmark = pytest.mark.skipif(not LIVE, reason="set MMC_LIVE=1 to run")


def test_brake_caliper_composes_multi_agent_flow():
    from mmc_agents.orchestrator.manager import run_plant_scenario
    from mmc_agents.orchestrator.scenarios.brake_caliper import (
        EXPECTED_BOUNDS,
        PROBLEM_STATEMENT,
    )

    async def _drive() -> list[dict]:
        out: list[dict] = []
        async for ev in run_plant_scenario("plant7", PROBLEM_STATEMENT):
            out.append(ev)
        return out

    events = asyncio.run(_drive())
    assert events, "no events emitted"

    agents_seen: set[str] = set()
    for ev in events:
        name = ev.get("agent")
        if name:
            agents_seen.add(name)

    print(f"\n{len(events)} events; agents seen: {agents_seen}")
    assert len(agents_seen) >= EXPECTED_BOUNDS["min_distinct_agents"], (
        f"Only {len(agents_seen)} agents seen: {agents_seen}"
    )
    must = EXPECTED_BOUNDS["must_include_agents"]
    missing = must - agents_seen
    assert not missing, f"Required agents missing from trace: {missing}"
