"""TraceEvent typed-model tests (Gate C, Task 2).

The TraceEvent model is the wire-format contract between the orchestrator
(`run_stream`), the FastAPI SSE backend, the static trace UI, and any future
recorder. Tests pin the JSON shape, optional-field defaults, and the gap that
motivates Gate C: per-turn agent reply text must be a first-class field.
"""

from __future__ import annotations

import json

import pytest

from mmc_agents.orchestrator.trace import TraceEvent, TraceEventType


def test_minimal_event_serializes_to_json():
    event = TraceEvent(run_id="run-1", sequence=0, type="start", message="begin")
    payload = event.model_dump(mode="json")

    assert payload["run_id"] == "run-1"
    assert payload["sequence"] == 0
    assert payload["type"] == "start"
    assert payload["message"] == "begin"
    # Optional fields default to None so the SSE stream is compact.
    assert payload["agent_name"] is None
    assert payload["content"] is None
    assert payload["task_ledger"] is None
    assert payload["progress_ledger"] is None
    assert payload["hop_index"] is None
    assert payload["metadata"] == {}
    # Timestamp is set automatically and is ISO-8601.
    assert isinstance(payload["timestamp"], str)
    assert payload["timestamp"].endswith("Z") or "+" in payload["timestamp"]


def test_agent_response_carries_reply_text():
    """Pre-review item 1: the demo UI needs per-turn agent replies."""
    event = TraceEvent(
        run_id="run-2",
        sequence=7,
        type="agent_response",
        message="p7-supplier-quality returned",
        agent_name="p7-supplier-quality",
        hop_index=3,
        content="BRK-CAL-XYZ has NO_DIRECT_ALT. Recommend ent-supply-chain.",
    )
    payload = event.model_dump(mode="json")

    assert payload["type"] == "agent_response"
    assert payload["agent_name"] == "p7-supplier-quality"
    assert payload["hop_index"] == 3
    assert payload["content"].startswith("BRK-CAL-XYZ")


def test_ledger_update_event_holds_structured_facts():
    event = TraceEvent(
        run_id="run-3",
        sequence=2,
        type="ledger_update",
        message="task ledger initialized",
        task_ledger={"facts": ["BRK-CAL-XYZ critical"], "open_questions": []},
        progress_ledger="Plan: supplier -> procurement -> demand",
    )

    assert event.task_ledger == {
        "facts": ["BRK-CAL-XYZ critical"],
        "open_questions": [],
    }
    assert event.progress_ledger.startswith("Plan:")


def test_backtrack_event_records_reason_in_metadata():
    event = TraceEvent(
        run_id="run-4",
        sequence=12,
        type="backtrack",
        message="NO_DIRECT_ALT observed; replanning",
        metadata={"reason": "NO_DIRECT_ALT", "from_agent": "p7-supplier-quality"},
    )

    assert event.metadata["reason"] == "NO_DIRECT_ALT"
    assert event.metadata["from_agent"] == "p7-supplier-quality"


def test_complete_event_carries_final_synthesis():
    event = TraceEvent(
        run_id="run-5",
        sequence=99,
        type="complete",
        message="run finished",
        content="Final recommendation: expedite SUP-001 ($8,880).",
    )

    assert event.type == "complete"
    assert "expedite" in event.content


def test_invalid_type_is_rejected():
    with pytest.raises(ValueError):
        TraceEvent(run_id="run-6", sequence=0, type="not-a-real-event", message="x")


def test_round_trip_preserves_field_order_and_values():
    """SSE payloads are JSON-serialized; ensure no data loss across the boundary."""
    original = TraceEvent(
        run_id="run-7",
        sequence=4,
        type="agent_call",
        message="dispatching ent-supply-chain",
        agent_name="ent-supply-chain",
        hop_index=2,
        metadata={"plan_step": 2, "project": "mmc-enterprise"},
    )
    raw = original.model_dump_json()
    decoded = TraceEvent.model_validate(json.loads(raw))

    assert decoded == original
    assert decoded.metadata["project"] == "mmc-enterprise"


def test_trace_event_type_literal_covers_expected_lifecycle():
    """Lock the allowed event types so SSE consumers can switch on them safely."""
    expected = {
        "start",
        "agent_call",
        "agent_response",
        "agent_no_data",
        "ledger_update",
        "backtrack",
        "complete",
        "error",
    }
    # TraceEventType is exported as an Iterable of literal strings (or equivalent).
    assert set(TraceEventType.__args__) == expected  # type: ignore[attr-defined]


def test_agent_no_data_event_is_a_first_class_outcome():
    """An empty-bodied executor_completed should be reportable as its own
    event type, not as an agent_response with content=None."""
    event = TraceEvent(
        run_id="run-no-data",
        sequence=4,
        type="agent_no_data",
        message="no matching content from ent-procurement",
        agent_name="ent-procurement",
        hop_index=3,
    )
    payload = event.model_dump(mode="json")

    assert payload["type"] == "agent_no_data"
    assert payload["agent_name"] == "ent-procurement"
    assert payload["hop_index"] == 3
    # The whole point of the new type: no content field needed; the message
    # carries the story.
    assert payload["content"] is None
