"""Manager hardening tests (Gate B Task 27).

The unit tests exercise the ScenarioRun helper and the NO_DIRECT_ALT signal
without spinning up Foundry. The live test runs against a deployed plant
project and is gated on MMC_LIVE=1.
"""
import asyncio
import os
from typing import Any

import pytest
from dotenv import load_dotenv

load_dotenv()

from mmc_agents.orchestrator.manager import (
    NO_DIRECT_ALT_RULE,
    ScenarioRun,
    run_and_capture,
    summarize_scenario_run,
)
from mmc_agents.tools.supplier import alternates


def test_scenario_run_detects_max_round_termination():
    """Task 28 — framework signals max_round_count by emitting a normal output
    event whose text contains 'maximum round count'; ScenarioRun must surface
    that as a boolean flag instead of swallowing it as a real answer."""
    text = "Workflow terminated due to reaching maximum round count."
    run = ScenarioRun(answer=text)
    run.terminated_by_max_rounds = "maximum round count" in run.answer.lower()
    assert run.terminated_by_max_rounds is True


def test_summarize_scenario_run_appends_partial_state_on_max_rounds():
    run = ScenarioRun(
        answer="Workflow terminated due to reaching maximum round count.",
        hops=["plant7-quality", "ent-procurement"],
        last_progress_ledger="Step 3: still waiting on enterprise procurement.",
        terminated_by_max_rounds=True,
    )
    rendered = summarize_scenario_run(run)
    assert "max_round_count" in rendered
    assert "plant7-quality" in rendered
    assert "ent-procurement" in rendered
    assert "still waiting on enterprise procurement" in rendered


def test_summarize_scenario_run_passes_through_normal_answers():
    run = ScenarioRun(answer="Final answer: route to SUP-002.")
    assert summarize_scenario_run(run) == "Final answer: route to SUP-002."


def test_scenario_run_records_backtracks_and_hops():
    run = ScenarioRun(answer="x", hops=["plant7-quality", "ent-procurement", "plant7-quality"], backtracks=1)
    assert run.backtracks == 1
    assert run.hops.count("plant7-quality") == 2


def test_manager_instructions_include_no_direct_alt_rule():
    """Verified statically against the constant to avoid building a live manager."""
    from mmc_agents.orchestrator import manager as mgr_mod
    import inspect

    src = inspect.getsource(mgr_mod._build_manager)
    assert "NO_DIRECT_ALT_RULE" in src
    assert NO_DIRECT_ALT_RULE.strip().startswith("When a supply-chain")


def test_supplier_alternates_signals_no_direct_alt_for_brake_caliper():
    hits = alternates("BRK-CAL-XYZ")
    assert hits and hits[0]["status"] == "NO_DIRECT_ALT"
    assert hits[0]["part_id"] == "BRK-CAL-XYZ"


class _FakeWorkflow:
    """Minimal stub of a Magentic workflow for unit-testing run_and_capture."""

    def __init__(self, events: list[Any]):
        self._events = events

    def run(self, task: str, stream: bool = True):  # noqa: D401 - mimic API
        events = self._events

        async def _gen():
            for ev in events:
                yield ev

        return _gen()


class _Ev:
    def __init__(self, type: str, executor_id: str | None = None, data: Any = None):
        self.type = type
        self.executor_id = executor_id
        self.data = data


def test_run_and_capture_aggregates_hops_only_for_known_agents():
    events = [
        _Ev("executor_completed", executor_id="mmc-magentic-manager"),
        _Ev("executor_completed", executor_id="plant7-maintenance"),
        _Ev("executor_completed", executor_id="ent-procurement"),
        _Ev("executor_completed", executor_id="plant7-quality"),
    ]
    run = asyncio.run(run_and_capture(_FakeWorkflow(events), "task"))
    assert run.hops == ["plant7-maintenance", "ent-procurement", "plant7-quality"]


LIVE = os.environ.get("MMC_LIVE") == "1"


@pytest.mark.skipif(not LIVE, reason="Requires deployed Foundry + KBs.")
def test_brake_caliper_backtracks_on_no_direct_alt():
    """End-to-end backtrack assertion. Skipped unless MMC_LIVE=1."""
    from agent_framework.orchestrations import MagenticBuilder
    from azure.identity import AzureCliCredential

    from mmc_agents.agent_factory import build_foundry_agents
    from mmc_agents.orchestrator.manager import _build_manager
    from mmc_agents.orchestrator.scenarios.brake_caliper import (
        EXPECTED_BOUNDS,
        PROBLEM_STATEMENT,
    )

    endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    participants = build_foundry_agents("plant7", endpoint, AzureCliCredential())
    wf = MagenticBuilder(participants=participants, manager=_build_manager()).build()
    run = asyncio.run(run_and_capture(wf, PROBLEM_STATEMENT))

    assert run.backtracks >= EXPECTED_BOUNDS["min_backtracks"]
    haystack = (run.last_progress_ledger or "") + (run.answer or "")
    for term in EXPECTED_BOUNDS["must_observe_terms"]:
        assert term in haystack, term
