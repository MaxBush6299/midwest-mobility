# src/mmc_agents/tools/fixtures_loader.py
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=64)
def _read(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding="utf-8"))

def load_fixture(path: str | Path, key: str) -> dict | None:
    return _read(str(path)).get(key)
