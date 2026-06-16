# src/mmc_agents/registry/base.py
from __future__ import annotations
from typing import Protocol
from pydantic import BaseModel

class AgentSkill(BaseModel):
    id: str
    description: str

class AgentCard(BaseModel):
    name: str                       # unique id, e.g. "plant7-ehs"
    display_name: str
    description: str
    endpoint: str                   # A2A endpoint (e.g. https://.../.well-known/agent-card.json)
    skills: list[AgentSkill]
    tier: str                       # "plant" | "enterprise"
    metadata: dict = {}

class RegistrySource(Protocol):
    def list_agents(self) -> list[AgentCard]: ...
