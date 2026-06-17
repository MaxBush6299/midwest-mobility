"""Tests for enterprise agent factory (Gate B Task 25)."""
from pathlib import Path

import yaml

from mmc_agents.agent_factory import emit_enterprise_agent_card
from mmc_agents.registry.base import AgentCard


def _profile():
    return yaml.safe_load(Path("enterprise/profile.yaml").read_text())


def test_emit_enterprise_card_procurement(tmp_path: Path):
    card = emit_enterprise_agent_card(
        _profile(),
        role="procurement",
        endpoint_base="http://localhost:8080",
        out_path=tmp_path / "agent.json",
    )
    assert card["name"] == "ent-procurement"
    assert card["tier"] == "enterprise"
    assert card["metadata"]["kb_sources"] == ["procurement"]
    assert card["metadata"]["tools"] == ["procurement"]
    AgentCard.model_validate(card)


def test_emit_writes_file(tmp_path: Path):
    out = tmp_path / "demand" / "agent.json"
    emit_enterprise_agent_card(
        _profile(),
        role="demand-program",
        endpoint_base="http://localhost:8080/",
        out_path=out,
    )
    assert out.is_file()
    assert out.read_text().endswith("\n")


def test_emit_endpoint_normalises_trailing_slash(tmp_path: Path):
    card = emit_enterprise_agent_card(
        _profile(),
        role="enterprise-quality",
        endpoint_base="http://localhost:8080/",
        out_path=tmp_path / "agent.json",
    )
    assert card["endpoint"] == (
        "http://localhost:8080/ent-quality/.well-known/agent-card.json"
    )
