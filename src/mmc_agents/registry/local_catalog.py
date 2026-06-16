# src/mmc_agents/registry/local_catalog.py
from __future__ import annotations
import json
from pathlib import Path
from mmc_agents.registry.base import AgentCard

class LocalCatalogSource:
    def __init__(self, catalog_path: Path):
        self.path = Path(catalog_path)
        self._cache: list[AgentCard] | None = None

    def list_agents(self) -> list[AgentCard]:
        if self._cache is None:
            self._cache = self._read()
        return self._cache

    def _read(self) -> list[AgentCard]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [AgentCard.model_validate(a) for a in data["agents"]]

class WatchedLocalCatalogSource(LocalCatalogSource):
    """Re-reads catalog.json on every list_agents() call. Powers hot-add demo."""
    def list_agents(self) -> list[AgentCard]:
        return self._read()
