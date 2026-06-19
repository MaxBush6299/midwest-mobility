"""Live smoke test for the multi-plant warranty scenario (Gate D Task 23).

Skipped unless MMC_LIVE=1. Requires deployed Foundry plant + enterprise KBs
and the plant7 + plant4 + enterprise agents registered as prompt agents.
"""
from __future__ import annotations

import asyncio
import os

import pytest
from dotenv import load_dotenv

load_dotenv()

LIVE = os.environ.get("MMC_LIVE", "0") == "1"

pytestmark = pytest.mark.skipif(
    not LIVE,
    reason="Requires deployed Foundry + KBs; set MMC_LIVE=1.",
)


def test_multi_plant_warranty_composes_cross_plant_flow():
    from azure.identity import AzureCliCredential
    from agent_framework.orchestrations import MagenticBuilder

    from mmc_agents.agent_factory import build_enterprise_agents, build_foundry_agents
    from mmc_agents.orchestrator.manager import _build_manager, run_and_capture
    from mmc_agents.orchestrator.scenarios.multi_plant_warranty import (
        EXPECTED_BOUNDS,
        PROBLEM_STATEMENT,
    )

    endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    plant4_endpoint = os.environ.get("FOUNDRY_PLANT4_PROJECT_ENDPOINT", endpoint)
    ent_endpoint = os.environ["FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT"]
    cred = AzureCliCredential()
    participants = (
        build_foundry_agents("plant7", endpoint, cred)
        + build_foundry_agents("plant4", plant4_endpoint, cred)
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
    haystack = run.last_progress_ledger + " " + run.answer
    haystack_upper = haystack.upper()
    for term in EXPECTED_BOUNDS.get("must_observe_terms", set()):
        assert term.upper() in haystack_upper, (
            f"Required term '{term}' missing from ledger and final answer"
        )
    answer = run.answer
    for plant_name in EXPECTED_BOUNDS.get("must_mention_plants", set()):
        assert plant_name in answer, (
            f"Final answer does not mention required plant '{plant_name}'"
        )
