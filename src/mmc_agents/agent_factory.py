"""Create/update portal-managed Foundry Prompt Agents from profile.yaml (Task 22).

Uses the *new* Foundry Agents Service (azure-ai-projects >= 2.2.0) at the
services.ai.azure.com endpoint. Each profile entry maps to a versioned
PromptAgentDefinition created via AIProjectClient.agents.create_version().

KB attachment: when <PLANT_ID_UPPER>_KB_CONNECTION_ID / <..>_KB_MCP_URL
(or the global PLANT_KB_CONNECTION_ID / PLANT_KB_MCP_URL) are set, the
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


def _kb_tool(plant_id: str | None = None) -> MCPTool | None:
    """Construct the Foundry IQ MCP tool for a plant, or None if unconfigured.

    Per-plant env vars take precedence over the legacy globals so each plant
    binds its own KB:

        <PLANT_ID_UPPER>_KB_CONNECTION_ID + <PLANT_ID_UPPER>_KB_MCP_URL
            e.g. PLANT4_KB_CONNECTION_ID / PLANT4_KB_MCP_URL

    Falls back to the global pair (PLANT_KB_CONNECTION_ID / PLANT_KB_MCP_URL)
    when either per-plant var is missing — this preserves Plant 7's
    pre-Gate-D behavior unchanged. Both vars in a pair must be set; a
    half-configured per-plant deploy falls back to the global pair rather
    than silently mixing connection ids from one plant with MCP URLs from
    another.
    """
    conn_id: str | None = None
    url: str | None = None
    if plant_id:
        pid = plant_id.upper()
        conn_id = os.environ.get(f"{pid}_KB_CONNECTION_ID")
        url = os.environ.get(f"{pid}_KB_MCP_URL")
        if not (conn_id and url):
            conn_id = url = None
    if not (conn_id and url):
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


def _load_enterprise_profile() -> dict:
    with open(ROOT / "enterprise" / "profile.yaml") as fh:
        return yaml.safe_load(fh)


def _instructions(
    plant_id: str,
    plant_display: str,
    agent_def: dict,
    language: str = "en",
) -> str:
    role = agent_def["role"]
    display = agent_def["display_name"]
    skills = "\n".join(
        f"  - {s['id']}: {s['description']}" for s in agent_def.get("skills", [])
    )
    kb_sources = ", ".join(agent_def.get("kb_sources", [])) or "(none assigned)"

    if language.lower().startswith("es"):
        kb_sources_label = kb_sources if kb_sources != "(none assigned)" else "(ninguna asignada)"
        return f"""Eres el agente {display} para {plant_display} (id: {plant_id}, rol: {role}).

Tus responsabilidades:
{skills}

Tienes acceso a una base de conocimiento de Foundry IQ que cubre: {kb_sources_label}.
SIEMPRE fundamenta tus respuestas en la base de conocimiento cuando esté disponible.
Cuando cites información, incluye el nombre del documento de origen. Si la recuperación
no devuelve nada relevante, responde "No pude encontrar esa información en mi base de
conocimiento" en lugar de adivinar.

Responde SIEMPRE en español, ya que tu base de conocimiento y tu planta operan en
español (Monterrey, MX).

Cuando tus fuentes incluyan tablas estructuradas (registros de capacitación, órdenes
de PM, incidentes, etc.), enumera CADA fila relevante listando explícitamente todos
los campos clave que devolvió la búsqueda — incluyendo Employee_ID, Employee_Name,
Training_Course, Completed_Date, Expiration_Date, Status, Trainer y cualquier otra
columna de fecha o de estado. Nunca digas "no se encontraron fechas de expiración"
si la fila recuperada contiene un valor de Expiration_Date; en cambio, transcríbelo
tal como aparece. Si una fila no tiene un campo, di explícitamente "campo vacío".

Estás participando en un flujo de trabajo multi-agente orquestado por un manager
Magentic. Mantente enfocado en tu rol; difiere al manager las preguntas fuera de tu
alcance para que las dirija al agente correcto."""

    return f"""You are the {display} agent for {plant_display} (id: {plant_id}, role: {role}).

Your responsibilities:
{skills}

You have access to a Foundry IQ knowledge base covering: {kb_sources}.
ALWAYS ground your answers in the knowledge base when available. When you cite
information, include the source document name. If retrieval returns nothing
relevant, say "I could not find that in my knowledge base" rather than guessing.

When your sources include structured tables (training records, PM orders,
incidents, etc.), enumerate EVERY relevant row and explicitly list all key
fields the search returned — including Employee_ID, Employee_Name,
Training_Course, Completed_Date, Expiration_Date, Status, Trainer and any
other date or status column. Never claim a field is missing if the retrieved
row carries a value; transcribe the value exactly as returned. If a row truly
has no value for a field, say "field empty" explicitly.

You are participating in a multi-agent workflow orchestrated by a Magentic
manager. Stay focused on your role; defer questions outside your scope to the
manager so it can route them to the right agent."""


def _upsert_version(
    client: AIProjectClient,
    name: str,
    description: str,
    instructions: str,
    kb_tool: MCPTool | None = None,
) -> AgentVersionDetails:
    tools = []
    if kb_tool is None:
        kb_tool = _kb_tool()
    if kb_tool is not None:
        tools.append(kb_tool)
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
    language = profile.get("language", "en")

    client = AIProjectClient(endpoint=project_endpoint, credential=credential)
    # Resolve KB tool once per plant so every agent version in the loop binds
    # to the same plant-scoped KB (or to the global fallback for Plant 7).
    kb = _kb_tool(plant_id)
    refs: list[PlantAgentRef] = []
    for agent_def in profile["agents"]:
        name = f"{plant_id}-{agent_def['role']}"
        description = agent_def["display_name"]
        instructions = _instructions(plant_id, plant_display, agent_def, language)

        version = _upsert_version(client, name, description, instructions, kb_tool=kb)
        refs.append(
            PlantAgentRef(
                name=name,
                description=description,
                version=getattr(version, "version", "?"),
                project_endpoint=project_endpoint,
            )
        )
    return refs


def _enterprise_instructions(enterprise_display: str, agent_def: dict) -> str:
    role = agent_def["role"]
    display = agent_def["display_name"]
    skills = "\n".join(
        f"  - {s['id']}: {s['description']}" for s in agent_def.get("skills", [])
    )
    kb_sources = ", ".join(agent_def.get("kb_sources", [])) or "(none assigned)"
    return f"""You are the {display} enterprise agent for {enterprise_display} (role: {role}).

Your responsibilities:
{skills}

You have access to a Foundry IQ knowledge base covering: {kb_sources}.
ALWAYS ground your answers in the knowledge base when available. When you cite
information, include the source document name. If retrieval returns nothing
relevant, say "I could not find that in my knowledge base" rather than guessing.

You are participating in a multi-agent workflow orchestrated by a Magentic
manager alongside plant-level agents. Stay focused on your enterprise role;
defer plant-specific operational questions back to the manager so it can route
them to the appropriate plant agent.

When the manager presents you with results from a plant-tier agent (for example
plant7-training or plant4-quality), treat those plant-cited rows as the
authoritative source for that plant. Do NOT attempt to re-validate plant-local
records by querying your own enterprise KB — your KB does not contain plant
operational logs (training records, PM schedules, incident logs, etc.). If a
plant agent's output appears incomplete (e.g., missing a column you need), ask
the manager to route a follow-up to that plant agent for the missing
projection; do not silently fall back to enterprise documents that look
superficially related."""


def upsert_enterprise_agents(
    project_endpoint: str,
    credential: TokenCredential,
) -> list[PlantAgentRef]:
    """Provision the 5 enterprise prompt agents on the enterprise Foundry project.

    Mirrors :func:`upsert_plant_agents` but reads ``enterprise/profile.yaml``
    and attaches the enterprise KB MCP tool (when ``ENTERPRISE_KB_CONNECTION_ID``
    / ``ENTERPRISE_KB_MCP_URL`` are set) instead of the plant tool.
    """
    profile = _load_enterprise_profile()
    enterprise_display = profile.get("display_name", "Enterprise")

    client = AIProjectClient(endpoint=project_endpoint, credential=credential)
    kb = _enterprise_kb_tool()
    refs: list[PlantAgentRef] = []
    for agent_def in profile["agents"]:
        name = agent_def["name"]
        description = agent_def["display_name"]
        instructions = _enterprise_instructions(enterprise_display, agent_def)

        version = _upsert_version(client, name, description, instructions, kb_tool=kb)
        refs.append(
            PlantAgentRef(
                name=name,
                description=description,
                version=getattr(version, "version", "?"),
                project_endpoint=project_endpoint,
            )
        )
    return refs


def build_enterprise_agents(
    project_endpoint: str,
    credential: TokenCredential,
) -> list["FoundryAgent"]:
    """Construct FoundryAgent participants for the 5 enterprise prompt agents.

    Does not provision — assumes :func:`upsert_enterprise_agents` has already
    created the portal agents on the enterprise Foundry project. Each returned
    FoundryAgent is bound to the latest version of its named portal agent.
    """
    if FoundryAgent is None:
        raise RuntimeError("agent_framework.foundry not installed")
    profile = _load_enterprise_profile()
    agents: list[FoundryAgent] = []
    for agent_def in profile["agents"]:
        name = agent_def["name"]
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
