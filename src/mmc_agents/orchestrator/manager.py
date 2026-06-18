"""Magentic orchestration over portal-managed Foundry agents (Task 26).

Gate B additions (Task 27 / 28):
- ScenarioRun dataclass + run_and_capture() helper for testable capture of
  hops, backtracks, plan text, progress ledger, and final synthesis.
- NO_DIRECT_ALT_RULE appended to the manager's instructions so it backtracks
  on supply-chain dead-ends instead of looping.

Gate C additions (Task 3):
- ``run_stream`` is the canonical event stream: it consumes
  ``workflow.run(task, stream=True)`` and emits typed ``TraceEvent`` objects
  for the FastAPI SSE relay, the demo UI, and tests.
- ``run_and_capture`` is now a thin collector that folds ``run_stream`` events
  into the existing ``ScenarioRun`` shape so Gate B tests are unchanged.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from agent_framework import Agent, AgentResponseUpdate
from agent_framework.orchestrations import (
    MagenticBuilder,
    MagenticOrchestratorEvent,
    MagenticOrchestratorEventType,
    StandardMagenticManager,
)
from azure.identity import AzureCliCredential

from mmc_agents.agent_factory import build_enterprise_agents, build_foundry_agents
from mmc_agents.observability import setup_tracing
from mmc_agents.orchestrator.model_config import manager_chat_client
from mmc_agents.orchestrator.trace import TraceEvent

_AGENT_ID_PREFIXES = ("plant", "p7-", "ent-")


NO_DIRECT_ALT_RULE = (
    " When a supply-chain or plant tool reports NO_DIRECT_ALT, treat it as a "
    "dead-end on that path, record the phrase in the progress ledger, and "
    "route the next turn to procurement, PLM, or demand to explore a different "
    "mitigation dimension."
)


def _build_manager(
    max_round_count: int = 15,
    max_stall_count: int = 3,
    max_reset_count: int = 2,
) -> StandardMagenticManager:
    base_instructions = (
        "You are the Magentic manager coordinating MMC plant and enterprise "
        "specialist agents. Pick the smallest set of agents needed, ground "
        "answers in their KB outputs, and produce a concise final synthesis. "
        "Converge quickly — once you have enough KB-grounded answers across "
        "the relevant agents (typically 4-6 rounds), STOP and emit the final "
        "answer. Do not request additional refinement once the answer is "
        "supported by the KB. "
        "If an agent replies that it cannot assist, that the data is not in "
        "its KB, that no records matched, that the requested entries are not "
        "available, or anything semantically equivalent (e.g., 'could not find', "
        "'not available in my KB', 'no matching records', 'KB does not contain'), "
        "ACCEPT that answer as terminal — do NOT keep redispatching "
        "to the same agent hoping for a different answer, and do NOT fan out "
        "to other agents in search of one. A negative-but-grounded answer is "
        "a valid final answer. Note the gap explicitly in the final synthesis "
        "and stop. Only re-dispatch when a *different specialist* can plausibly "
        "answer a *different sub-question*, never to retry the same gap."
    )
    planner = Agent(
        client=manager_chat_client(),
        instructions=base_instructions + NO_DIRECT_ALT_RULE,
        name="mmc-magentic-manager",
    )
    return StandardMagenticManager(
        agent=planner,
        max_round_count=max_round_count,
        max_stall_count=max_stall_count,
        max_reset_count=max_reset_count,
        final_answer_prompt=(
            "Produce the final answer for the user. Synthesize the plant and "
            "enterprise agents' KB-grounded responses into a single concise "
            "recommendation that directly addresses the original task. Preserve "
            "the agents' source citations (e.g., file names) so the user can "
            "trace claims to the KB. "
            "Structure: (1) Direct answer in 1-2 sentences, (2) Key supporting "
            "facts with citations, (3) Recommended next steps."
        ),
    )


@dataclass
class ScenarioRun:
    """Aggregated capture of a Magentic workflow run for hardening tests."""

    answer: str = ""
    hops: list[str] = field(default_factory=list)
    backtracks: int = 0
    plan_text: str = ""
    last_progress_ledger: str = ""
    terminated_by_max_rounds: bool = False


def _is_agent_executor(executor_id: str | None) -> bool:
    return bool(executor_id) and executor_id.startswith(_AGENT_ID_PREFIXES)


def _extract_text(data: Any) -> str:
    """Best-effort text extraction from agent_framework event payloads.

    Handles the shapes the orchestrator emits across event types:
    - ``AgentExecutorResponse`` — workflow wrapper around the agent's full
      reply. Its ``.agent_response`` is an ``AgentResponse`` whose ``.text``
      property already concatenates all message contents correctly. This is
      the **canonical full reply** for an executor_completed event.
    - ``AgentResponse``: ``.text`` property, or ``.messages[-1].text``.
    - ``Message``: ``.text`` property, or concatenated ``.contents[*].text``.
    - Lists (executor_completed packs ``sent_messages + yielded_outputs`` as
      a list, where the first item is the AgentExecutorResponse wrapper and
      the tail is streaming AgentResponseUpdate chunks) — recurse into each
      item and return the longest non-empty extraction so the wrapper's
      complete text wins over partial streaming chunks or annotation-only
      events (which carry ``【N:M†source】`` markers but empty body text).
    - ``AgentResponseUpdate`` and similar single objects with ``.text`` or
      ``.contents``.

    Returns ``""`` when nothing is extractable.
    """
    if data is None:
        return ""

    if isinstance(data, (list, tuple)):
        best = ""
        for item in data:
            t = _extract_text(item)
            if t and len(t) > len(best):
                best = t
        return best

    inner = getattr(data, "agent_response", None)
    if inner is not None:
        t = _extract_text(inner)
        if t:
            return t

    t = getattr(data, "text", None)
    if isinstance(t, str) and t:
        return t

    msgs = getattr(data, "messages", None)
    if msgs:
        joined = " ".join(
            (getattr(m, "text", "") or "") for m in msgs
        ).strip()
        if joined:
            return joined
        last = msgs[-1]
        cs = getattr(last, "contents", None) or []
        joined = "".join(getattr(c, "text", "") or "" for c in cs)
        if joined:
            return joined

    cs = getattr(data, "contents", None) or []
    if cs:
        return "".join(getattr(c, "text", "") or "" for c in cs)

    return ""


def _dump_payload(executor_id: str | None, data: Any) -> None:
    """Debug helper: dump executor_completed data structure to a file.

    Enable with ``MMC_DEBUG_DUMP_PAYLOAD=1``. Appends one entry per call to
    ``mmc_debug_payload.log`` in the cwd. Captures item types, attributes,
    and ``repr()`` so we can see why ``_extract_text`` is missing content.
    """
    import pathlib, time
    log = pathlib.Path("mmc_debug_payload.log")
    lines: list[str] = []
    lines.append(f"\n=== {time.strftime('%H:%M:%S')} executor={executor_id} ===")
    lines.append(f"top-level type: {type(data).__name__}")
    items = data if isinstance(data, (list, tuple)) else [data]
    lines.append(f"item count: {len(items)}")
    for i, it in enumerate(items):
        lines.append(f"  [{i}] type={type(it).__name__} attrs={[a for a in dir(it) if not a.startswith('_')][:20]}")
        t = getattr(it, "text", None)
        lines.append(f"      .text={t!r}")
        msgs = getattr(it, "messages", None)
        if msgs:
            lines.append(f"      .messages len={len(msgs)} last.text={getattr(msgs[-1], 'text', None)!r}")
            cs = getattr(msgs[-1], "contents", None) or []
            for j, c in enumerate(cs):
                lines.append(f"        msg.contents[{j}] type={type(c).__name__} text={getattr(c, 'text', None)!r}")
        cs = getattr(it, "contents", None) or []
        for j, c in enumerate(cs):
            lines.append(f"      .contents[{j}] type={type(c).__name__} text={getattr(c, 'text', None)!r}")
    log.write_text(log.read_text(encoding="utf-8") + "\n".join(lines) if log.exists() else "\n".join(lines), encoding="utf-8")


async def run_stream(
    workflow,
    *,
    run_id: str,
    task: str,
) -> AsyncIterator[TraceEvent]:
    """Drive ``workflow.run(task, stream=True)`` and yield typed TraceEvents.

    Event mapping:
    - ``start`` is emitted once with the problem statement.
    - ``executor_invoked`` for plant/enterprise agent IDs -> ``agent_call``.
    - ``executor_completed`` for plant/enterprise agent IDs -> ``agent_response``
      carrying the reply text.
    - ``MagenticOrchestratorEvent`` with PLAN_CREATED or PROGRESS_LEDGER_UPDATED
      -> ``ledger_update``; REPLANNED -> ``backtrack``.
    - ``output`` -> ``complete`` carrying the final synthesis.
    """
    seq = 0

    def _next(**kwargs: Any) -> TraceEvent:
        nonlocal seq
        ev = TraceEvent(run_id=run_id, sequence=seq, **kwargs)
        seq += 1
        return ev

    yield _next(type="start", message=task)

    hop_index = 0
    final_text = ""

    async for ev in workflow.run(task, stream=True):
        evtype = str(getattr(ev, "type", ""))
        data = getattr(ev, "data", None)
        executor_id = getattr(ev, "executor_id", None)

        if isinstance(data, MagenticOrchestratorEvent):
            text = getattr(getattr(data, "content", None), "text", "") or ""
            etype = data.event_type
            if etype == MagenticOrchestratorEventType.PLAN_CREATED:
                yield _next(
                    type="ledger_update",
                    message="plan created",
                    task_ledger={"plan": text},
                )
            elif etype == MagenticOrchestratorEventType.REPLANNED:
                yield _next(
                    type="backtrack",
                    message="manager replanned",
                    metadata={"replan_text": text[:500]},
                )
            elif etype == MagenticOrchestratorEventType.PROGRESS_LEDGER_UPDATED:
                yield _next(
                    type="ledger_update",
                    message="progress ledger updated",
                    progress_ledger=text,
                )

        if evtype == "executor_invoked" and _is_agent_executor(executor_id):
            hop_index += 1
            yield _next(
                type="agent_call",
                message=f"dispatching {executor_id}",
                agent_name=executor_id,
                hop_index=hop_index,
            )
        elif evtype == "executor_completed" and _is_agent_executor(executor_id):
            if os.environ.get("MMC_DEBUG_DUMP_PAYLOAD"):
                _dump_payload(executor_id, data)
            text = _extract_text(data)
            if text:
                yield _next(
                    type="agent_response",
                    message=f"{executor_id} responded",
                    agent_name=executor_id,
                    hop_index=hop_index,
                    content=text,
                )
            else:
                # The executor completed but no narrative reply text was
                # extractable — typically annotation-only chunks ("【N:M†source】")
                # or an empty body that says "no matching records". Surface as
                # a first-class no-data event so the UI can render it with a
                # distinct treatment instead of an empty agent_response card.
                yield _next(
                    type="agent_no_data",
                    message=f"no matching content from {executor_id}",
                    agent_name=executor_id,
                    hop_index=hop_index,
                )
        elif evtype == "output":
            final_text = _extract_text(data)

    yield _next(type="complete", message="run finished", content=final_text)


async def run_and_capture(workflow, task: str) -> ScenarioRun:
    """Collector over ``run_stream`` that produces a Gate B ``ScenarioRun``.

    Hops are recorded from ``agent_response`` and ``agent_no_data`` events
    (both represent an executor that ran); backtracks from ``backtrack``
    events; plan/progress ledger from ``ledger_update`` events; final
    synthesis from the terminal ``complete`` event. ``run_id`` is a stable
    per-call value because the tests only care about field aggregation, not
    run identity.
    """
    out = ScenarioRun()
    async for event in run_stream(workflow, run_id="capture", task=task):
        if event.type in ("agent_response", "agent_no_data") and event.agent_name:
            out.hops.append(event.agent_name)
        elif event.type == "backtrack":
            out.backtracks += 1
        elif event.type == "ledger_update":
            if event.task_ledger and "plan" in event.task_ledger:
                out.plan_text = event.task_ledger["plan"]
            if event.progress_ledger:
                out.last_progress_ledger = event.progress_ledger
        elif event.type == "complete":
            out.answer = event.content or ""

    out.terminated_by_max_rounds = "maximum round count" in out.answer.lower()
    return out


def summarize_scenario_run(run: ScenarioRun) -> str:
    """Render a ScenarioRun for demo/UI consumers, exposing partial state
    when the manager hit ``max_round_count`` before converging (Task 28)."""
    body = run.answer or "(no answer captured)"
    if run.terminated_by_max_rounds:
        body += (
            "\n\n[Manager hit max_round_count before converging. "
            f"Hops so far: {run.hops}. "
            f"Last progress ledger: {run.last_progress_ledger[:300]}]"
        )
    return body


async def run_plant_scenario(plant_id: str, task: str) -> AsyncIterator[dict]:
    """Stream Magentic events for a plant scenario. Yields {kind, agent, text|data}.

    Participants always include the named plant's agents plus all 5 enterprise
    agents (when ``FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT`` is set), so backtrack
    flows like brake-caliper / LOTO can route into enterprise procurement, PLM,
    quality, and demand.
    """
    setup_tracing()
    cred = AzureCliCredential()
    endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    participants = build_foundry_agents(plant_id, endpoint, cred)
    ent_endpoint = os.environ.get("FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT")
    if ent_endpoint:
        participants = participants + build_enterprise_agents(ent_endpoint, cred)

    workflow = (
        MagenticBuilder(
            participants=participants,
            manager=_build_manager(),
        )
        .build()
    )

    from opentelemetry import trace

    tracer = trace.get_tracer("mmc_agents.orchestrator")
    with tracer.start_as_current_span(f"magentic.scenario.{plant_id}") as span:
        span.set_attribute("mmc.plant_id", plant_id)
        span.set_attribute("mmc.task", task[:500])
        async for ev in workflow.run(task, stream=True):
            evtype = getattr(ev, "type", None)
            executor_id = getattr(ev, "executor_id", None)
            data = getattr(ev, "data", None)

            agent_name: str | None = None
            if executor_id and (
                executor_id.startswith(f"{plant_id}-") or executor_id.startswith("ent-")
            ):
                agent_name = executor_id
            elif hasattr(data, "participant_name"):
                agent_name = getattr(data, "participant_name", None)

            yield {
                "kind": str(evtype),
                "agent": agent_name,
                "executor": executor_id,
                "data_type": type(data).__name__ if data is not None else None,
            }
