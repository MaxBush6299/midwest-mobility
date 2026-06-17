"""Tests for enterprise agent factory (Gate B Tasks 25 & 26)."""
import json
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
    assert card["metadata"]["kb_sources"] == ["procurement", "po_data"]
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


_SNAPSHOT_DIR = Path("tests/snapshots/enterprise_agent_cards")
_ROLE_SNAPSHOTS = {
    "supply-chain": "supply-chain.agent.json",
    "procurement": "procurement.agent.json",
    "engineering-plm": "engineering-plm.agent.json",
    "enterprise-quality": "enterprise-quality.agent.json",
    "demand-program": "demand-program.agent.json",
}


def test_factory_emitted_enterprise_cards_match_snapshots(tmp_path: Path):
    """Each role's factory output must equal the committed snapshot exactly
    (Gate B Task 26 — factory is single source of truth for enterprise cards)."""
    profile = _profile()
    for role, snapshot_name in _ROLE_SNAPSHOTS.items():
        out = tmp_path / role / "agent.json"
        emitted = emit_enterprise_agent_card(
            profile, role, "http://localhost:8080", out
        )
        expected = json.loads((_SNAPSHOT_DIR / snapshot_name).read_text())
        assert emitted == expected, role
