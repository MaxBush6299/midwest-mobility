"""Emit A2A AgentCard JSON for plant agents (Foundry-backed) and enterprise
agents (profile-backed, no Foundry calls).

For plants: calls upsert_plant_agents() (idempotent) and writes one card per
Foundry agent into plants/<plant>/cards/.

For enterprise: reads enterprise/profile.yaml and writes one card per role into
enterprise/<node>/agent.json via emit_enterprise_agent_card() so the factory is
the single source of truth (Gate B Task 26).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import yaml
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from mmc_agents.agent_factory import emit_enterprise_agent_card, upsert_plant_agents

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent

# Map enterprise role -> on-disk node directory name.
_ENTERPRISE_NODES = {
    "supply-chain": "supply-chain",
    "procurement": "procurement",
    "engineering-plm": "engineering-plm",
    "enterprise-quality": "enterprise-quality",
    "demand-program": "demand-program",
}


def _emit_plant_cards() -> int:
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
            "agent_id": r.name,
            "version": r.version,
            "skills": [],
            "metadata": {"plant_id": plant_id, "project": "mmc-plant"},
        }
        (out_dir / f"{r.name}.json").write_text(json.dumps(card, indent=2))
        print(f"wrote plant {r.name}.json (version={r.version})")
    return len(refs)


def _emit_enterprise_cards(endpoint_base: str = "http://localhost:8080") -> int:
    profile = yaml.safe_load((ROOT / "enterprise" / "profile.yaml").read_text())
    count = 0
    for role, node in _ENTERPRISE_NODES.items():
        out = ROOT / "enterprise" / node / "agent.json"
        emit_enterprise_agent_card(profile, role, endpoint_base, out)
        print(f"wrote enterprise {out.relative_to(ROOT)}")
        count += 1
    return count


def main() -> int:
    if os.environ.get("FOUNDRY_PLANT_PROJECT_ENDPOINT"):
        _emit_plant_cards()
    else:
        print("FOUNDRY_PLANT_PROJECT_ENDPOINT not set; skipping plant cards.")
    endpoint_base = os.environ.get(
        "ENTERPRISE_CARD_ENDPOINT_BASE", "http://localhost:8080"
    )
    _emit_enterprise_cards(endpoint_base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
