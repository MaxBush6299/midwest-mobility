"""In-memory run store with queue fan-out for SSE subscribers.

Design:
- Each run owns a ``RunSession`` with:
  - an asyncio buffer (``list[TraceEvent]``) — late subscribers replay from this
  - an asyncio ``Event`` (``completed``) flipped when the run finishes
  - a list of per-subscriber asyncio queues for live fan-out
- ``RunStore.create_run`` schedules an async producer (``_drive``) that
  iterates a user-supplied ``ScenarioRunner`` and pushes events to every
  subscriber queue.
- ``subscribe`` yields buffered events first, then live events; closes when the
  run completes.

A ``ScenarioRunner`` is any callable
``(run_id: str, scenario: ScenarioId, task: str | None) -> AsyncIterator[TraceEvent]``.
Production uses ``live_scenario_runner`` (wired to the orchestrator);
tests inject a fake to avoid hitting Foundry.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import uuid
from dataclasses import dataclass, field
from typing import AsyncIterator, Awaitable, Callable

from mmc_agents.orchestrator.trace import TraceEvent
from mmc_agents.trace_ui.schemas import ScenarioId

logger = logging.getLogger(__name__)

ScenarioRunner = Callable[[str, ScenarioId, str | None], AsyncIterator[TraceEvent]]


@dataclass
class RunSession:
    run_id: str
    scenario: ScenarioId
    task: str | None
    buffer: list[TraceEvent] = field(default_factory=list)
    subscribers: list[asyncio.Queue[TraceEvent | None]] = field(default_factory=list)
    completed: asyncio.Event = field(default_factory=asyncio.Event)
    error: str | None = None


class RunStore:
    """Owns active and recent ``RunSession`` objects."""

    def __init__(self, runner: ScenarioRunner, max_runs: int = 32) -> None:
        self._runner = runner
        self._max_runs = max_runs
        self._sessions: dict[str, RunSession] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}

    def create_run(self, scenario: ScenarioId, task: str | None = None) -> RunSession:
        run_id = uuid.uuid4().hex[:12]
        session = RunSession(run_id=run_id, scenario=scenario, task=task)
        self._sessions[run_id] = session
        self._evict_if_needed()
        self._tasks[run_id] = asyncio.create_task(
            self._drive(session), name=f"run-{run_id}"
        )
        return session

    def get(self, run_id: str) -> RunSession | None:
        return self._sessions.get(run_id)

    async def subscribe(self, run_id: str) -> AsyncIterator[TraceEvent]:
        session = self._sessions.get(run_id)
        if session is None:
            return
        queue: asyncio.Queue[TraceEvent | None] = asyncio.Queue()
        # Replay buffered events for late subscribers.
        for event in list(session.buffer):
            await queue.put(event)
        # Register for live events only if the run is still in flight.
        if not session.completed.is_set():
            session.subscribers.append(queue)
        else:
            await queue.put(None)

        try:
            while True:
                event = await queue.get()
                if event is None:
                    return
                yield event
                if event.type in {"complete", "error"}:
                    return
        finally:
            if queue in session.subscribers:
                session.subscribers.remove(queue)

    async def shutdown(self) -> None:
        for task in list(self._tasks.values()):
            task.cancel()
        for task in list(self._tasks.values()):
            with contextlib.suppress(BaseException):
                await task

    async def _drive(self, session: RunSession) -> None:
        try:
            async for event in self._runner(session.run_id, session.scenario, session.task):
                session.buffer.append(event)
                for queue in list(session.subscribers):
                    await queue.put(event)
                if event.type in {"complete", "error"}:
                    break
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("run %s failed", session.run_id)
            session.error = str(exc)
            error_event = TraceEvent(
                run_id=session.run_id,
                sequence=len(session.buffer),
                type="error",
                message=f"run failed: {exc}",
            )
            session.buffer.append(error_event)
            for queue in list(session.subscribers):
                await queue.put(error_event)
        finally:
            session.completed.set()
            for queue in list(session.subscribers):
                await queue.put(None)

    def _evict_if_needed(self) -> None:
        if len(self._sessions) <= self._max_runs:
            return
        # Drop the oldest completed run to bound memory.
        for rid, sess in list(self._sessions.items()):
            if sess.completed.is_set():
                self._sessions.pop(rid, None)
                self._tasks.pop(rid, None)
                if len(self._sessions) <= self._max_runs:
                    return
