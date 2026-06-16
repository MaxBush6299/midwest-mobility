"""Magentic orchestration over portal-managed Foundry agents (Task 26)."""
from __future__ import annotations

import os
from typing import AsyncIterator

from agent_framework import Agent, AgentResponseUpdate
from agent_framework.orchestrations import (
    MagenticBuilder,
    MagenticOrchestratorEvent,
    StandardMagenticManager,
)
from azure.identity import AzureCliCredential

from mmc_agents.agent_factory import build_foundry_agents
from mmc_agents.observability import setup_tracing
from mmc_agents.orchestrator.model_config import manager_chat_client


def _build_manager() -> StandardMagenticManager:
    planner = Agent(
        client=manager_chat_client(),
        instructions=(
            "You are the Magentic manager coordinating MMC plant specialist agents. "
            "Pick the smallest set of agents needed, ground answers in their KB outputs, "
            "and produce a concise final synthesis. Converge quickly — once you have "
            "enough KB-grounded answers across the relevant plant agents (typically 4-6 "
            "rounds), STOP and emit the final answer. Do not request additional "
            "refinement once the answer is supported by the KB."
        ),
        name="mmc-magentic-manager",
    )
    return StandardMagenticManager(
        agent=planner,
        max_round_count=15,
        max_stall_count=3,
        max_reset_count=2,
        final_answer_prompt=(
            "Produce the final answer for the user. Synthesize the plant agents' "
            "KB-grounded responses into a single concise recommendation that directly "
            "addresses the original task. Preserve the agents' source citations "
            "(e.g., file names) so the user can trace claims to the KB. "
            "Structure: (1) Direct answer in 1-2 sentences, (2) Key supporting facts "
            "with citations, (3) Recommended next steps."
        ),
    )


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
