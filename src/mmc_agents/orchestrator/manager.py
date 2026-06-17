"""Magentic orchestration over portal-managed Foundry agents (Task 26).

Gate B Task 27 additions:
- ScenarioRun dataclass + run_and_capture() helper for testable capture of
  hops, backtracks, plan text, progress ledger, and final synthesis.
- NO_DIRECT_ALT_RULE appended to the manager's instructions so it backtracks
  on supply-chain dead-ends instead of looping.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import AsyncIterator

from agent_framework import Agent, AgentResponseUpdate
from agent_framework.orchestrations import (
    MagenticBuilder,
    MagenticOrchestratorEvent,
    MagenticOrchestratorEventType,
    StandardMagenticManager,
)
from azure.identity import AzureCliCredential

from mmc_agents.agent_factory import build_foundry_agents
from mmc_agents.observability import setup_tracing
from mmc_agents.orchestrator.model_config import manager_chat_client


NO_DIRECT_ALT_RULE = (
    " When a supply-chain or plant tool reports NO_DIRECT_ALT, treat it as a "
    "dead-end on that path, record the phrase in the progress ledger, and "
    "route the next turn to procurement, PLM, or demand to explore a different "
    "mitigation dimension."
)


def _build_manager() -> StandardMagenticManager:
    base_instructions = (
        "You are the Magentic manager coordinating MMC plant and enterprise "
        "specialist agents. Pick the smallest set of agents needed, ground "
        "answers in their KB outputs, and produce a concise final synthesis. "
        "Converge quickly — once you have enough KB-grounded answers across "
        "the relevant agents (typically 4-6 rounds), STOP and emit the final "
        "answer. Do not request additional refinement once the answer is "
        "supported by the KB."
    )
    planner = Agent(
        client=manager_chat_client(),
        instructions=base_instructions + NO_DIRECT_ALT_RULE,
        name="mmc-magentic-manager",
    )
    return StandardMagenticManager(
        agent=planner,
        max_round_count=15,
        max_stall_count=3,
        max_reset_count=2,
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


async def run_and_capture(workflow, task: str) -> ScenarioRun:
    """Drive ``workflow.run(task, stream=True)`` and aggregate a ScenarioRun.

    Hops are recorded on ``executor_completed`` events whose ``executor_id``
    starts with ``plant`` or ``ent-``. Backtracks are counted from
    ``MagenticOrchestratorEvent`` with event_type=REPLANNED. The final
    synthesis is harvested from WorkflowEvent type=='output'.
    """
    out = ScenarioRun()
    async for ev in workflow.run(task, stream=True):
        evtype = str(getattr(ev, "type", ""))
        data = getattr(ev, "data", None)
        executor_id = getattr(ev, "executor_id", None)

        if (
            evtype == "executor_completed"
            and executor_id
            and (executor_id.startswith("plant") or executor_id.startswith("ent-"))
        ):
            out.hops.append(executor_id)

        if isinstance(data, MagenticOrchestratorEvent):
            text = getattr(getattr(data, "content", None), "text", "") or ""
            if data.event_type == MagenticOrchestratorEventType.PLAN_CREATED:
                out.plan_text = text
            elif data.event_type == MagenticOrchestratorEventType.REPLANNED:
                out.backtracks += 1
            elif data.event_type == MagenticOrchestratorEventType.PROGRESS_LEDGER_UPDATED:
                out.last_progress_ledger = text

        if evtype == "output":
            msgs = getattr(data, "messages", None)
            if msgs:
                last = msgs[-1]
                t = getattr(last, "text", None)
                if t:
                    out.answer += t
                else:
                    cs = getattr(last, "contents", None) or []
                    out.answer += "".join(getattr(c, "text", str(c)) for c in cs)
            else:
                cs = getattr(data, "contents", None) or []
                out.answer += "".join(getattr(c, "text", str(c)) for c in cs)

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
    """Stream Magentic events for a plant scenario. Yields {kind, agent, text|data}."""
    setup_tracing()
    cred = AzureCliCredential()
    endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    participants = build_foundry_agents(plant_id, endpoint, cred)

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
            if executor_id and executor_id.startswith(f"{plant_id}-"):
                agent_name = executor_id
            elif hasattr(data, "participant_name"):
                agent_name = getattr(data, "participant_name", None)

            yield {
                "kind": str(evtype),
                "agent": agent_name,
                "executor": executor_id,
                "data_type": type(data).__name__ if data is not None else None,
            }
