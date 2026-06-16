"""Manager-side model client for the Magentic planner (Task 25)."""
from __future__ import annotations

import os

from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


def manager_chat_client() -> FoundryChatClient:
    # Manager prefers a dedicated deployment so it doesn't share quota with the plant agents.
    deployment = (
        os.environ.get("FOUNDRY_MANAGER_DEPLOYMENT")
        or os.environ.get("FOUNDRY_MODEL_DEPLOYMENT", "gpt-5.4-mini")
    )
    return FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"],
        model=deployment,
        credential=AzureCliCredential(),
    )
