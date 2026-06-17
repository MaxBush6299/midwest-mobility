"""Tests for ``run_stream`` (Gate C, Task 3).

We avoid hitting Foundry by driving the orchestrator with a fake workflow that
yields the same shape of events the real one does. The contract under test is:

- ``run_stream`` yields ``TraceEvent`` objects in sequence order.
- ``start`` is always first, ``complete`` is always last.
- An ``executor_invoked`` for a plant/enterprise agent produces ``agent_call``;
  the matching ``executor_completed`` produces ``agent_response`` carrying the
  reply text, with the same ``hop_index``.
- Magentic manager events become ``ledger_update`` / ``backtrack``.
- ``run_and_capture`` (refactored to a collector over ``run_stream``) keeps the
  same ``ScenarioRun`` shape used by Gate B's hardening tests.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from mmc_agents.orchestrator.manager import ScenarioRun, run_and_capture, run_stream
from mmc_agents.orchestrator.trace import TraceEvent


class _FakeManagerEvent:
    """Stand-in for ``MagenticOrchestratorEvent`` with the fields the manager reads."""

    def __init__(self, event_type: Any, text: str):
        self.event_type = event_type
        self.content = SimpleNamespace(text=text)


class _FakeManagerEventType:
    PLAN_CREATED = "PLAN_CREATED"
    REPLANNED = "REPLANNED"
    PROGRESS_LEDGER_UPDATED = "PROGRESS_LEDGER_UPDATED"


class _FakeMessage:
    def __init__(self, text: str):
        self.text = text


class _FakeOutput:
    def __init__(self, text: str):
        self.messages = [_FakeMessage(text)]


class _FakeWorkflow:
    """Yields a canned scripted event sequence and ignores ``task`` content."""

    def __init__(self, events: list[Any]):
        self._events = events

    async def run(self, task: str, stream: bool = True):  # noqa: ARG002
        for ev in self._events:
            yield ev


def _ev(evtype: str, *, executor_id: str | None = None, data: Any = None):
    return SimpleNamespace(type=evtype, executor_id=executor_id, data=data)


@pytest.fixture(autouse=True)
def _patch_manager_event_types(monkeypatch):
    """Make the manager's MagenticOrchestratorEvent isinstance check accept our fake.

    The manager module imports ``MagenticOrchestratorEvent`` and
    ``MagenticOrchestratorEventType`` from agent_framework; we replace the
    isinstance target and the enum so the test can use lightweight fakes.
    """
    from mmc_agents.orchestrator import manager as mod

    monkeypatch.setattr(mod, "MagenticOrchestratorEvent", _FakeManagerEvent)
    monkeypatch.setattr(mod, "MagenticOrchestratorEventType", _FakeManagerEventType)


def _scripted_events():
    return [
        _ev(
            "magentic_event",
            data=_FakeManagerEvent(_FakeManagerEventType.PLAN_CREATED, "supplier -> proc"),
        ),
        _ev("executor_invoked", executor_id="p7-supplier-quality"),
        _ev(
            "executor_completed",
            executor_id="p7-supplier-quality",
            data=_FakeOutput("BRK-CAL-XYZ NO_DIRECT_ALT"),
        ),
        _ev(
            "magentic_event",
            data=_FakeManagerEvent(_FakeManagerEventType.REPLANNED, "switch to procurement"),
        ),
        _ev("executor_invoked", executor_id="ent-procurement"),
        _ev(
            "executor_completed",
            executor_id="ent-procurement",
            data=_FakeOutput("SUP-001 expedite $8,880"),
        ),
        _ev(
            "magentic_event",
            data=_FakeManagerEvent(
                _FakeManagerEventType.PROGRESS_LEDGER_UPDATED, "ledger: 2 hops"
            ),
        ),
        _ev("output", data=_FakeOutput("Recommendation: expedite SUP-001.")),
    ]


@pytest.mark.asyncio
async def test_run_stream_emits_typed_trace_events_in_order():
    workflow = _FakeWorkflow(_scripted_events())
    events: list[TraceEvent] = []
    async for ev in run_stream(workflow, run_id="run-stream-1", task="brake-caliper"):
        events.append(ev)

    # Sequence numbers are monotonic from 0.
    assert [e.sequence for e in events] == list(range(len(events)))
    assert events[0].type == "start"
    assert events[0].message == "brake-caliper"
    assert events[-1].type == "complete"
    assert events[-1].content == "Recommendation: expedite SUP-001."


@pytest.mark.asyncio
async def test_run_stream_pairs_call_and_response_with_same_hop_index():
    workflow = _FakeWorkflow(_scripted_events())
    events = [e async for e in run_stream(workflow, run_id="run-stream-2", task="t")]

    calls = [e for e in events if e.type == "agent_call"]
    responses = [e for e in events if e.type == "agent_response"]

    assert [c.agent_name for c in calls] == ["p7-supplier-quality", "ent-procurement"]
    assert [r.agent_name for r in responses] == ["p7-supplier-quality", "ent-procurement"]
    assert [c.hop_index for c in calls] == [1, 2]
    assert [r.hop_index for r in responses] == [1, 2]
    # Reply text must be present — this is the Gate C visibility gap.
    assert "NO_DIRECT_ALT" in responses[0].content
    assert "SUP-001" in responses[1].content


@pytest.mark.asyncio
async def test_run_stream_emits_ledger_and_backtrack_events():
    workflow = _FakeWorkflow(_scripted_events())
    events = [e async for e in run_stream(workflow, run_id="run-stream-3", task="t")]

    ledger_events = [e for e in events if e.type == "ledger_update"]
    backtrack_events = [e for e in events if e.type == "backtrack"]

    # Plan + progress ledger -> 2 ledger updates.
    assert len(ledger_events) == 2
    assert any("supplier" in (e.task_ledger or {}).get("plan", "") for e in ledger_events)
    assert any("ledger: 2 hops" in (e.progress_ledger or "") for e in ledger_events)

    assert len(backtrack_events) == 1
    assert "switch to procurement" in backtrack_events[0].metadata.get("replan_text", "")


@pytest.mark.asyncio
async def test_run_stream_ignores_non_plant_executor_ids():
    workflow = _FakeWorkflow([
        _ev("executor_invoked", executor_id="manager"),
        _ev("executor_completed", executor_id="manager", data=_FakeOutput("noise")),
        _ev("output", data=_FakeOutput("done")),
    ])
    events = [e async for e in run_stream(workflow, run_id="run-stream-4", task="t")]

    # Only start + complete should fire; the manager executor is filtered out.
    assert [e.type for e in events] == ["start", "complete"]


@pytest.mark.asyncio
async def test_run_and_capture_collects_from_run_stream_unchanged_shape():
    """Gate B's tests still rely on ScenarioRun — keep its public shape stable."""
    workflow = _FakeWorkflow(_scripted_events())
    run: ScenarioRun = await run_and_capture(workflow, task="brake-caliper")

    assert run.hops == ["p7-supplier-quality", "ent-procurement"]
    assert run.backtracks == 1
    assert "supplier -> proc" in run.plan_text
    assert "ledger: 2 hops" in run.last_progress_ledger
    assert run.answer == "Recommendation: expedite SUP-001."
    assert run.terminated_by_max_rounds is False


@pytest.mark.asyncio
async def test_run_stream_extracts_text_from_list_data():
    """executor_completed wraps `sent_messages + yielded_outputs` as a list.

    In streaming mode the list contains many partial AgentResponseUpdate
    chunks plus the final assembled message; we want the full reply, not
    a vertical character salad. Regression: live trace showed each token
    rendered on its own line because chunks were joined with newlines.
    """
    full = "BRK-CAL-XYZ has NO_DIRECT_ALT per supplier.alternates()."
    events = [
        _ev("executor_invoked", executor_id="p7-supplier-quality"),
        _ev(
            "executor_completed",
            executor_id="p7-supplier-quality",
            # Streaming chunks (partial prefixes) + the final full message.
            data=[
                _FakeOutput("BRK"),
                _FakeOutput("BRK-CAL-XYZ"),
                _FakeOutput("BRK-CAL-XYZ has NO_DIRECT_ALT"),
                _FakeOutput(full),
            ],
        ),
        _ev("output", data=_FakeOutput("done")),
    ]
    out = [e async for e in run_stream(_FakeWorkflow(events), run_id="r", task="t")]
    responses = [e for e in out if e.type == "agent_response"]
    assert responses, "agent_response event missing"
    # Full reply wins, no token-by-token splitting.
    assert responses[0].content == full
