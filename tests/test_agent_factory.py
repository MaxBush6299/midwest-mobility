import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("MMC_LIVE") != "1", reason="live Azure test; set MMC_LIVE=1 to run"
)


def test_upsert_plant7_agents_creates_five():
    from azure.identity import AzureCliCredential
    from dotenv import load_dotenv

    load_dotenv()
    from mmc_agents.agent_factory import upsert_plant_agents

    agents = upsert_plant_agents(
        "plant7",
        project_endpoint=os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"],
        credential=AzureCliCredential(),
    )
    names = {a.name for a in agents}
    assert names == {
        "plant7-ehs",
        "plant7-maintenance",
        "plant7-quality",
        "plant7-shiftops",
        "plant7-training",
    }
    for a in agents:
        assert a.version, f"{a.name} missing version"