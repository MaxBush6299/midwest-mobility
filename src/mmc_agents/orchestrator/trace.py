"""Typed trace events emitted by the Magentic orchestrator (Gate C).

`TraceEvent` is the wire-format contract shared by:

- `mmc_agents.orchestrator.manager.run_stream` (producer)
- `mmc_agents.trace_ui.app` (FastAPI SSE relay)
- `src/mmc_agents/trace_ui/static/index.html` (vanilla-JS consumer)
- `tests/test_trace_events.py` / `tests/test_manager_run_stream.py`

Design notes:
- Events are Pydantic v2 models so the SSE payloads are valid JSON without
  custom serializers.
- `agent_response.content` is intentionally first-class — Gate B's
  `ScenarioRun` only captured executor IDs and the final synthesis; the trace
  UI needs the per-turn reply text to be useful to a viewer.
- Optional fields default to None so the SSE stream stays compact; absence
  encodes "not applicable for this event type."
- `sequence` is a monotonic integer the producer assigns; consumers use it to
  detect drops or reorder.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

TraceEventType = Literal[
    "start",
    "agent_call",
    "agent_response",
    "ledger_update",
    "backtrack",
    "complete",
    "error",
]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TraceEvent(BaseModel):
    """One event in a streaming Magentic run.

    Field semantics by event type:
    - ``start``         — run accepted; ``message`` carries the problem statement.
    - ``agent_call``    — manager dispatches to ``agent_name`` at ``hop_index``.
    - ``agent_response``— agent replied; ``content`` carries the reply text.
    - ``ledger_update`` — task and/or progress ledger refreshed.
    - ``backtrack``     — manager replanned; ``metadata['reason']`` (e.g.
      ``"NO_DIRECT_ALT"``) should be set.
    - ``complete``      — run finished; ``content`` carries the final synthesis.
    - ``error``         — terminal failure; ``message`` is human-readable.
    """

    model_config = ConfigDict(extra="forbid")

    run_id: str
    sequence: int = Field(ge=0)
    type: TraceEventType
    message: str
    timestamp: datetime = Field(default_factory=_utcnow)
    agent_name: str | None = None
    hop_index: int | None = None
    content: str | None = None
    task_ledger: dict[str, Any] | None = None
    progress_ledger: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
