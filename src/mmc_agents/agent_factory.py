"""Create/update portal-managed Foundry agents from profile.yaml (Task 22).

Idempotent upsert via azure-ai-agents AgentsClient: for each agent in
plants/{plant}/profile.yaml we either create a new Foundry agent on the
service or update the existing one (keyed by name). Returns FoundryAgent
wrappers ready for the Magentic orchestrator.

Agents are created without KB tools — operators attach Foundry IQ kb-plant7
through the Foundry portal (Task 22b). This is intentional: it keeps
agent_factory free of preview-SDK MCP plumbing and makes "swap the KB in
the portal" a documented Day-2 operation.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from agent_framework.foundry import FoundryAgent, FoundryAgentOptions
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import Agent
from azure.core.credentials import TokenCredential

ROOT = Path(__file__).resolve().parent.parent.parent
MODEL = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4o-mini")


def _load_profile(plant_id: str) -> dict:
    with open(ROOT / "plants" / plant_id / "profile.yaml") as fh:
        return yaml.safe_load(fh)


def _instructions(plant_id: str, plant_display: str, agent_def: dict) -> str:
    role = agent_def["role"]
    display = agent_def["display_name"]
    skills = "\n".join(
        f"  - {s['id']}: {s['description']}" for s in agent_def.get("skills", [])
    )
    kb_sources = ", ".join(agent_def.get("kb_sources", [])) or "(none assigned)"
    return f"""You are the {display} agent for {plant_display} (id: {plant_id}, role: {role}).

Your responsibilities:
{skills}

You have access to a Foundry IQ knowledge base covering: {kb_sources}.
ALWAYS ground your answers in the knowledge base when available. When you cite
information, include the source document name. If retrieval returns nothing
relevant, say "I could not find that in my knowledge base" rather than guessing.

You are participating in a multi-agent workflow orchestrated by a Magentic
manager. Stay focused on your role; defer questions outside your scope to the
manager so it can route them to the right agent."""


def _upsert_one(
    client: AgentsClient,
    existing: dict[str, Agent],
    name: str,
    description: str,
    instructions: str,
) -> Agent:
    if name in existing:
        return client.update_agent(
            agent_id=existing[name].id,
            model=MODEL,
            name=name,
            description=description,
            instructions=instructions,
        )
    return client.create_agent(
        model=MODEL,
        name=name,
        description=description,
        instructions=instructions,
    )


def upsert_plant_agents(
    plant_id: str,
    project_endpoint: str,
    credential: TokenCredential,
) -> list[FoundryAgent]:
    profile = _load_profile(plant_id)
    plant_display = profile.get("display_name", plant_id)

    client = AgentsClient(endpoint=project_endpoint, credential=credential)
    existing = {a.name: a for a in client.list_agents() if a.name}

    real_agents: list[Agent] = []
    for agent_def in profile["agents"]:
        name = f"{plant_id}-{agent_def['role']}"
        real_agents.append(
            _upsert_one(
                client,
                existing,
                name=name,
                description=agent_def["display_name"],
                instructions=_instructions(plant_id, plant_display, agent_def),
            )
        )

    return [
        FoundryAgent(
            project_endpoint=project_endpoint,
            credential=credential,
            agent_name=a.name,
            name=a.name,
            description=a.description,
            default_options=FoundryAgentOptions(model=MODEL),
        )
        for a in real_agents
    ]

