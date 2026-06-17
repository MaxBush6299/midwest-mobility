"""Live smoke test for the Safety/LOTO cluster scenario (Gate B Task 30).

Skipped unless MMC_LIVE=1. Requires deployed Foundry plant + enterprise KBs
and the 10-agent pool (5 plant + 5 enterprise) registered as prompt agents.
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


def test_loto_cluster_composes_distinct_flow():
    from azure.identity import AzureCliCredential
    from agent_framework.orchestrations import MagenticBuilder

    from mmc_agents.agent_factory import build_enterprise_agents, build_foundry_agents
    from mmc_agents.orchestrator.manager import _build_manager, run_and_capture
    from mmc_agents.orchestrator.scenarios.loto_cluster import (
        EXPECTED_BOUNDS,
        PROBLEM_STATEMENT,
    )

    endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    ent_endpoint = os.environ["FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT"]
    cred = AzureCliCredential()
    participants = build_foundry_agents("plant7", endpoint, cred) + build_enterprise_agents(
        ent_endpoint, cred
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
    for term in EXPECTED_BOUNDS["must_observe_terms"]:
        assert term in run.answer.upper(), (
            f"Required term '{term}' missing from final answer: {run.answer[:500]}"
        )
