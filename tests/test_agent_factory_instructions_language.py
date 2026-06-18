"""Tests for language-aware agent instructions in agent_factory._instructions.

Plant 4 (profile.yaml language: es) should receive Spanish instructions so
the agent reasons and responds in the same language as its KB content.
Plant 7 (language: en, the default) must remain unchanged.
"""

from __future__ import annotations

from mmc_agents.agent_factory import _instructions


_AGENT_DEF = {
    "role": "ehs",
    "display_name": "Plant 4 EHS / Safety",
    "kb_sources": ["ehs", "incident_data"],
    "skills": [
        {"id": "hazard_loto_lookup", "description": "Hazard & LOTO requirement lookup"},
    ],
}


def test_english_instructions_unchanged_when_language_is_en() -> None:
    text = _instructions(
        plant_id="plant7",
        plant_display="MMC Plant 7 (Cincinnati, OH)",
        agent_def=_AGENT_DEF,
        language="en",
    )
    assert "You are the" in text
    assert "Your responsibilities:" in text
    assert "Foundry IQ knowledge base" in text
    # No Spanish leakage
    assert "Eres el" not in text
    assert "Tus responsabilidades" not in text


def test_english_instructions_default_when_language_omitted() -> None:
    """Backwards compatibility: callers that don't pass language get English."""
    text = _instructions(
        plant_id="plant7",
        plant_display="MMC Plant 7 (Cincinnati, OH)",
        agent_def=_AGENT_DEF,
    )
    assert "You are the" in text
    assert "Eres el" not in text


def test_spanish_instructions_when_language_is_es() -> None:
    text = _instructions(
        plant_id="plant4",
        plant_display="MMC Plant 4 (Monterrey, MX)",
        agent_def=_AGENT_DEF,
        language="es",
    )
    # Spanish opener and section headings
    assert "Eres el" in text or "Eres la" in text
    assert "responsabilidades" in text.lower()
    # KB grounding instruction translated
    assert "base de conocimiento" in text.lower()
    # No English leakage of the key sentences
    assert "You are the" not in text
    assert "Your responsibilities:" not in text
    # Plant display name still substituted
    assert "MMC Plant 4 (Monterrey, MX)" in text
    # Role and skill ID still surfaced
    assert "ehs" in text
    assert "hazard_loto_lookup" in text


def test_spanish_includes_no_knowledge_fallback_phrasing() -> None:
    """The 'I could not find that in my knowledge base' fallback must be
    translated so the agent responds in Spanish when KB retrieval misses."""
    text = _instructions(
        plant_id="plant4",
        plant_display="MMC Plant 4 (Monterrey, MX)",
        agent_def=_AGENT_DEF,
        language="es",
    )
    # Either of the natural Spanish phrasings is acceptable
    assert "no pude encontrar" in text.lower() or "no encontré" in text.lower()
