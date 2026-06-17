"""Create/update portal-managed Foundry Prompt Agents from profile.yaml (Task 22).

Uses the *new* Foundry Agents Service (azure-ai-projects >= 2.2.0) at the
services.ai.azure.com endpoint. Each profile entry maps to a versioned
PromptAgentDefinition created via AIProjectClient.agents.create_version().

KB attachment: when PLANT_KB_CONNECTION_ID / PLANT_KB_MCP_URL are set, the
factory attaches the Foundry IQ MCP tool to every agent so every new version
includes the KB binding (idempotent — no portal step required).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentVersionDetails,
    MCPTool,
    PromptAgentDefinition,
)
from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceNotFoundError

try:
    from agent_framework.foundry import FoundryAgent
except Exception:  # pragma: no cover - allow import without agent_framework
    FoundryAgent = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parent.parent.parent


def _model() -> str:
    """Read model deployment lazily so .env loaded after import still wins."""
    return os.environ.get("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4o-mini")


def _kb_tool() -> MCPTool | None:
    """Construct the Foundry IQ MCP tool from env, or None if unconfigured."""
    conn_id = os.environ.get("PLANT_KB_CONNECTION_ID")
    url = os.environ.get("PLANT_KB_MCP_URL")
    if not (conn_id and url):
        return None
    return MCPTool(
        server_label=conn_id,
        server_url=url,
        require_approval="never",
        project_connection_id=conn_id,
    )


def _enterprise_kb_tool() -> MCPTool | None:
    """Construct the enterprise Foundry IQ MCP tool from env, or None."""
    conn_id = os.environ.get("ENTERPRISE_KB_CONNECTION_ID")
    url = os.environ.get("ENTERPRISE_KB_MCP_URL")
    if not (conn_id and url):
        return None
    return MCPTool(
        server_label=conn_id,
        server_url=url,
        require_approval="never",
        project_connection_id=conn_id,
    )


def emit_enterprise_agent_card(
    profile: dict,
    role: str,
    endpoint_base: str,
    out_path: Path,
) -> dict:
    """Emit a single AgentCard JSON for an enterprise role from profile.yaml.

    Writes the card to ``out_path`` (parents created) and returns the dict.
    Matches the schema of hand-authored ``enterprise/<node>/agent.json`` files
    so snapshots can verify parity (Gate B Task 25/26).
    """
    import json

    agent_def = next(a for a in profile["agents"] if a["role"] == role)
    name = agent_def["name"]
    display = agent_def["display_name"]
    description = agent_def.get("description") or f"{display} enterprise agent."
    card = {
        "name": name,
        "display_name": display,
        "description": description,
        "endpoint": f"{endpoint_base.rstrip('/')}/{name}/.well-known/agent-card.json",
        "skills": agent_def["skills"],
        "tier": "enterprise",
        "metadata": {
            "kb_sources": agent_def["kb_sources"],
            "tools": agent_def["tools"],
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    return card


@dataclass
class PlantAgentRef:
    """Reference to a portal-managed prompt agent (returned by the factory)."""

    name: str
    description: str
    version: str
    project_endpoint: str

    @property
    def display(self) -> str:
        return f"{self.name}@{self.version}"


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


def _upsert_version(
    client: AIProjectClient,
    name: str,
    description: str,
    instructions: str,
) -> AgentVersionDetails:
    tools = []
    kb = _kb_tool()
    if kb is not None:
        tools.append(kb)
    definition = PromptAgentDefinition(
        model=_model(),
        instructions=instructions,
        tools=tools or None,
    )

    version = client.agents.create_version(
        agent_name=name,
        definition=definition,
        description=description,
    )
    return version


def build_foundry_agents(
    plant_id: str,
    project_endpoint: str,
    credential: TokenCredential,
) -> list["FoundryAgent"]:
    """Construct FoundryAgent participants for Magentic from profile.yaml.

    Does not provision — assumes upsert_plant_agents() has already created
    the portal agents. Each returned FoundryAgent is bound to the latest
    version of its named portal agent.
    """
    if FoundryAgent is None:
        raise RuntimeError("agent_framework.foundry not installed")
    profile = _load_profile(plant_id)
    agents: list[FoundryAgent] = []
    for agent_def in profile["agents"]:
        name = f"{plant_id}-{agent_def['role']}"
        agents.append(
            FoundryAgent(
                project_endpoint=project_endpoint,
                agent_name=name,
                credential=credential,
                name=name,
                description=agent_def["display_name"],
            )
        )
    return agents


def upsert_plant_agents(
    plant_id: str,
    project_endpoint: str,
    credential: TokenCredential,
) -> list[PlantAgentRef]:
    profile = _load_profile(plant_id)
    plant_display = profile.get("display_name", plant_id)

    client = AIProjectClient(endpoint=project_endpoint, credential=credential)
    refs: list[PlantAgentRef] = []
    for agent_def in profile["agents"]:
        name = f"{plant_id}-{agent_def['role']}"
        description = agent_def["display_name"]
        instructions = _instructions(plant_id, plant_display, agent_def)

        version = _upsert_version(client, name, description, instructions)
        refs.append(
            PlantAgentRef(
                name=name,
                description=description,
                version=getattr(version, "version", "?"),
                project_endpoint=project_endpoint,
            )
        )
    return refs
