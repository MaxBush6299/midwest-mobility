"""Live smoke test for the brake-caliper Magentic scenario.

Gate A (Task 28) established baseline composition; Gate B (Task 31) tightened
the assertions to use ``run_and_capture`` so we can verify that the full
10-agent pool composes a real cross-tier answer to BRK-CAL-XYZ.

Gate D (Task 22) extends the participants to include Plant 4 and asserts a
cross-plant composition: at least one Plant 4 plant-local hop must appear and
the final answer must mention both Plant 7 and Plant 4.

Backtracks are now expected to be 0 — with the enterprise pool present the
manager plans correctly upfront. See ``scenarios/brake_caliper.py`` for the
full rationale.

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
    from azure.identity import AzureCliCredential
    from agent_framework.orchestrations import MagenticBuilder

    from mmc_agents.agent_factory import build_enterprise_agents, build_foundry_agents
    from mmc_agents.orchestrator.manager import _build_manager, run_and_capture
    from mmc_agents.orchestrator.scenarios.brake_caliper import (
        EXPECTED_BOUNDS,
        PROBLEM_STATEMENT,
    )

    endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    ent_endpoint = os.environ["FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT"]
    cred = AzureCliCredential()
    participants = (
        build_foundry_agents("plant7", endpoint, cred)
        + build_foundry_agents("plant4", endpoint, cred)
        + build_enterprise_agents(ent_endpoint, cred)
    )
    workflow = MagenticBuilder(
        participants=participants, manager=_build_manager()
    ).build()

    run = asyncio.run(run_and_capture(workflow, PROBLEM_STATEMENT))
    distinct = set(run.hops)

    print(f"\nHops: {run.hops}")
    print(f"Backtracks: {run.backtracks}; terminated_by_max_rounds={run.terminated_by_max_rounds}")

    assert len(distinct) >= EXPECTED_BOUNDS["min_distinct_agents"], (
        f"Only {len(distinct)} distinct agents in trace: {distinct}"
    )
    must = EXPECTED_BOUNDS["must_include_agents"]
    missing = must - distinct
    assert not missing, f"Required agents missing from trace: {missing}"
    for alternatives in EXPECTED_BOUNDS.get("must_include_any", []):
        assert distinct & alternatives, (
            f"None of {alternatives} appeared in trace: {distinct}"
        )
    assert run.backtracks >= EXPECTED_BOUNDS["min_backtracks"], (
        f"Expected >= {EXPECTED_BOUNDS['min_backtracks']} backtracks, got {run.backtracks}"
    )
    haystack_upper = (run.last_progress_ledger + " " + run.answer).upper()
    for term in EXPECTED_BOUNDS.get("must_observe_terms", set()):
        assert term.upper() in haystack_upper, (
            f"Required term '{term}' missing from ledger and final answer"
        )
    answer = run.answer
    for plant_name in EXPECTED_BOUNDS.get("must_mention_plants", set()):
        assert plant_name in answer, (
            f"Final answer does not mention required plant '{plant_name}'"
        )

