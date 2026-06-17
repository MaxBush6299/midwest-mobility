"""Upsert the 5 enterprise prompt agents on the enterprise Foundry project.

Mirrors ``generate_cards.py``'s plant-side ``upsert_plant_agents`` call but
targets ``FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT`` and the enterprise profile.

Idempotent: each agent is upserted as a new version on its named portal agent.
Run again after wiring ``ENTERPRISE_KB_CONNECTION_ID`` / ``ENTERPRISE_KB_MCP_URL``
so the new version includes the Foundry IQ MCP tool binding.
"""
from __future__ import annotations

import os
import sys

from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from mmc_agents.agent_factory import upsert_enterprise_agents


def main() -> int:
    load_dotenv()
    endpoint = os.environ.get("FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT")
    if not endpoint:
        print("FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT not set; aborting.", file=sys.stderr)
        return 2

    kb_wired = bool(
        os.environ.get("ENTERPRISE_KB_CONNECTION_ID")
        and os.environ.get("ENTERPRISE_KB_MCP_URL")
    )
    print(f"target endpoint: {endpoint}")
    print(f"enterprise KB MCP tool: {'attached' if kb_wired else 'NOT attached (env vars unset)'}")

    refs = upsert_enterprise_agents(endpoint, AzureCliCredential())
    for r in refs:
        print(f"  {r.name} -> version {r.version}")
    print(f"upserted {len(refs)} enterprise agents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
