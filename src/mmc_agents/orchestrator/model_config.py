"""Manager-side model client for the Magentic planner (Task 25)."""
from __future__ import annotations

import os

from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


def manager_chat_client() -> FoundryChatClient:
    return FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL_DEPLOYMENT", "gpt-5.4-mini"),
        credential=AzureCliCredential(),
    )
