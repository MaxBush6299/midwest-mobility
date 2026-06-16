"""Emit A2A AgentCard JSON for each plant agent created in Foundry (Task 23).

Calls upsert_plant_agents() (idempotent) and writes one card per agent. Cards
are consumed by mmc_agents.registry.LocalCatalogSource.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from mmc_agents.agent_factory import upsert_plant_agents

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    plant_id = "plant7"
    endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    refs = upsert_plant_agents(plant_id, endpoint, AzureCliCredential())

    out_dir = ROOT / "plants" / plant_id / "cards"
    out_dir.mkdir(parents=True, exist_ok=True)
    for r in refs:
        card = {
            "schema_version": "1",
            "name": r.name,
            "description": r.description,
            "endpoint": endpoint,
            "agent_id": r.name,  # new SDK identifies agents by name; versions are separate
            "version": r.version,
            "skills": [],
            "metadata": {"plant_id": plant_id, "project": "mmc-plant"},
        }
        (out_dir / f"{r.name}.json").write_text(json.dumps(card, indent=2))
        print(f"wrote {r.name}.json (version={r.version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
