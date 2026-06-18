"""Per-plant Foundry IQ KB env lookup for agent_factory._kb_tool().

Gate D Task 21 — the factory must resolve KB connection + MCP URL
from per-plant env vars (e.g. PLANT4_KB_CONNECTION_ID /
PLANT4_KB_MCP_URL) so each plant's agents are bound to that plant's
KB. The legacy globals (PLANT_KB_CONNECTION_ID / PLANT_KB_MCP_URL)
must keep working as a fallback so Plant 7 onboarding does not
regress.
"""
from __future__ import annotations

import pytest


# The factory imports azure-ai-projects MCPTool at module load; keep
# imports inside tests so the test file is collectable without that
# dependency in environments where the package isn't fully installed.


def test_kb_tool_uses_per_plant_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """plant4 env vars must take precedence over the global PLANT_* vars."""
    monkeypatch.setenv("PLANT_KB_CONNECTION_ID", "global-conn")
    monkeypatch.setenv("PLANT_KB_MCP_URL", "https://global/mcp")
    monkeypatch.setenv("PLANT4_KB_CONNECTION_ID", "plant4-conn")
    monkeypatch.setenv("PLANT4_KB_MCP_URL", "https://plant4/mcp")

    from mmc_agents.agent_factory import _kb_tool

    tool = _kb_tool("plant4")
    assert tool is not None
    assert tool.server_label == "plant4-conn"
    assert tool.server_url == "https://plant4/mcp"


def test_kb_tool_falls_back_to_global_for_plant7(monkeypatch: pytest.MonkeyPatch) -> None:
    """plant7 keeps using the global PLANT_KB_* env vars when per-plant ones
    are unset — back-compat with Gate A/B/C deployments."""
    monkeypatch.setenv("PLANT_KB_CONNECTION_ID", "global-conn")
    monkeypatch.setenv("PLANT_KB_MCP_URL", "https://global/mcp")
    monkeypatch.delenv("PLANT7_KB_CONNECTION_ID", raising=False)
    monkeypatch.delenv("PLANT7_KB_MCP_URL", raising=False)

    from mmc_agents.agent_factory import _kb_tool

    tool = _kb_tool("plant7")
    assert tool is not None
    assert tool.server_label == "global-conn"
    assert tool.server_url == "https://global/mcp"


def test_kb_tool_returns_none_when_neither_per_plant_nor_global_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PLANT_KB_CONNECTION_ID", raising=False)
    monkeypatch.delenv("PLANT_KB_MCP_URL", raising=False)
    monkeypatch.delenv("PLANT4_KB_CONNECTION_ID", raising=False)
    monkeypatch.delenv("PLANT4_KB_MCP_URL", raising=False)

    from mmc_agents.agent_factory import _kb_tool

    assert _kb_tool("plant4") is None


def test_kb_tool_partial_per_plant_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """If only one of the per-plant pair is set, fall back to the global
    pair rather than mixing the two — prevents a half-configured deploy from
    silently sending traffic to the wrong KB."""
    monkeypatch.setenv("PLANT_KB_CONNECTION_ID", "global-conn")
    monkeypatch.setenv("PLANT_KB_MCP_URL", "https://global/mcp")
    monkeypatch.setenv("PLANT4_KB_CONNECTION_ID", "plant4-conn")
    monkeypatch.delenv("PLANT4_KB_MCP_URL", raising=False)

    from mmc_agents.agent_factory import _kb_tool

    tool = _kb_tool("plant4")
    assert tool is not None
    assert tool.server_label == "global-conn"
    assert tool.server_url == "https://global/mcp"
