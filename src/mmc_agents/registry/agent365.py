# src/mmc_agents/registry/agent365.py
"""End-state registry source: Microsoft Agent 365 (Graph API, preview).

Not implemented in the thin slice (D9). Keep this seam in the code so swapping
to Agent 365 later is purely additive.
"""
from __future__ import annotations
from mmc_agents.registry.base import AgentCard

class Agent365Source:
    def __init__(self, tenant_id: str | None = None):
        self.tenant_id = tenant_id

    def list_agents(self) -> list[AgentCard]:
        # TODO(swap-in): replace with Graph API call to Agent 365 registry once tenant access is available.
        raise NotImplementedError("Agent365Source is a documented future swap-in. Use LocalCatalogSource.")
