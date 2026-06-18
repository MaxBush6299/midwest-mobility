"""HTTP-level tests for the Gate C FastAPI trace UI.

A fake ``ScenarioRunner`` is injected so the tests never touch Foundry. The
fake yields a canned sequence of ``TraceEvent`` objects mimicking a
brake-caliper run. We use ``httpx.AsyncClient`` against the ASGI app directly
(no live server).
"""

from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator

import httpx
import pytest
from httpx import ASGITransport

from mmc_agents.orchestrator.trace import TraceEvent
from mmc_agents.trace_ui.app import create_app


def _make_scripted_runner(delay: float = 0.0):
    async def runner(run_id: str, scenario: str, task: str | None) -> AsyncIterator[TraceEvent]:
        yield TraceEvent(run_id=run_id, sequence=0, type="start", message=task or scenario)
        yield TraceEvent(
            run_id=run_id,
            sequence=1,
            type="agent_call",
            message="dispatching p7-supplier-quality",
            agent_name="p7-supplier-quality",
            hop_index=1,
        )
        if delay:
            await asyncio.sleep(delay)
        yield TraceEvent(
            run_id=run_id,
            sequence=2,
            type="agent_response",
            message="p7-supplier-quality responded",
            agent_name="p7-supplier-quality",
            hop_index=1,
            content="BRK-CAL-XYZ NO_DIRECT_ALT",
        )
        yield TraceEvent(
            run_id=run_id,
            sequence=3,
            type="complete",
            message="run finished",
            content="Recommendation: expedite SUP-001.",
        )

    return runner


@pytest.fixture
def client() -> AsyncIterator[httpx.AsyncClient]:
    app = create_app(runner=_make_scripted_runner())
    transport = ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


async def _async_client(runner=None) -> tuple[httpx.AsyncClient, object]:
    app = create_app(runner=runner or _make_scripted_runner())
    transport = ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver"), app


async def test_list_agents_returns_full_catalog():
    client, _ = await _async_client()
    async with client:
        resp = await client.get("/agents")
    assert resp.status_code == 200
    body = resp.json()
    names = [a["name"] for a in body["agents"]]
    tiers = {a["tier"] for a in body["agents"]}
    assert len(names) == 16, f"expected 16 agents (Gate D: + plant4 roster), got {len(names)}: {names}"
    assert tiers == {"plant", "enterprise"}
    assert "plant7-external-auditor" in names
    assert "plant4-ehs" in names


async def test_create_run_returns_run_id_and_events_url():
    client, _ = await _async_client()
    async with client:
        resp = await client.post("/runs", json={"scenario": "brake_caliper"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["scenario"] == "brake_caliper"
    assert len(body["run_id"]) >= 8
    assert body["events_url"].endswith(f"/runs/{body['run_id']}/events")


async def test_create_run_rejects_unknown_scenario():
    client, _ = await _async_client()
    async with client:
        resp = await client.post("/runs", json={"scenario": "nonsense"})
    assert resp.status_code == 422


async def test_events_stream_replays_buffered_then_completes():
    """Subscribe AFTER the run has finished — buffered events must replay in order."""
    client, _ = await _async_client()
    async with client:
        post = await client.post("/runs", json={"scenario": "brake_caliper"})
        run_id = post.json()["run_id"]
        # Give the background task a moment to finish (no real I/O in the fake).
        await asyncio.sleep(0.05)

        events: list[dict] = []
        async with client.stream("GET", f"/runs/{run_id}/events") as resp:
            assert resp.status_code == 200
            assert resp.headers["content-type"].startswith("text/event-stream")
            async for line in resp.aiter_lines():
                if line.startswith("data:"):
                    events.append(json.loads(line[len("data:") :].strip()))

    types = [e["type"] for e in events]
    assert types == ["start", "agent_call", "agent_response", "complete"]
    assert [e["sequence"] for e in events] == [0, 1, 2, 3]
    assert events[2]["content"] == "BRK-CAL-XYZ NO_DIRECT_ALT"
    assert events[-1]["content"].startswith("Recommendation")


async def test_events_endpoint_404_for_unknown_run():
    client, _ = await _async_client()
    async with client:
        resp = await client.get("/runs/does-not-exist/events")
    assert resp.status_code == 404


async def test_blast_radius_returns_unavailable_for_unknown_agent():
    """Unknown agents return available=False with an explanation, no 5xx."""
    client, _ = await _async_client()
    async with client:
        resp = await client.get("/agents/p7-supplier-quality/blast-radius")
    assert resp.status_code == 200
    body = resp.json()
    assert body["agent"] == "p7-supplier-quality"
    assert body["available"] is False
    assert "p7-supplier-quality" in (body["detail"] or "")


async def test_blast_radius_returns_real_graph_for_known_agent():
    """Real agent returns full governance graph with edges and revocation effects."""
    client, _ = await _async_client()
    async with client:
        resp = await client.get("/agents/plant7-training/blast-radius")
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is True
    assert body["agent"] == "plant7-training"
    assert body["foundry_project"] == "mmc-plant"
    assert body["knowledge_base"] == "kb-plant7"
    edge_kinds = {e["kind"] for e in body["edges"]}
    # Must include the full chain so the demo can show every revocation lever.
    assert {"foundry_project", "knowledge_base", "kb_source", "search_service", "sql_server"} <= edge_kinds
    # Every edge must carry a revocation_effect string so the UI can render the
    # "🔒 Revoke:" call-out — that's the entire point of the overlay.
    assert all(e["revocation_effect"] for e in body["edges"])


async def test_hot_add_rejects_already_persisted_agent():
    client, _ = await _async_client()
    async with client:
        resp = await client.post(
            "/demo/hot-add", json={"name": "plant7-external-auditor"}
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted"] is False
    assert "already in the persisted catalog" in body["detail"]


async def test_hot_add_rejects_agent_outside_shadow_catalog():
    client, _ = await _async_client()
    async with client:
        resp = await client.post(
            "/demo/hot-add", json={"name": "plant7-totally-made-up"}
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted"] is False
    assert "hot-add catalog" in body["detail"]


async def test_hot_add_pulls_shadow_agent_onto_stage_and_appears_in_list():
    client, _ = await _async_client()
    async with client:
        before = (await client.get("/agents")).json()["agents"]
        names_before = {a["name"] for a in before}
        assert "plant7-supplier-quality" not in names_before

        resp = await client.post(
            "/demo/hot-add", json={"name": "plant7-supplier-quality"}
        )
        body = resp.json()
        assert body["accepted"] is True
        assert body["agent"]["name"] == "plant7-supplier-quality"
        assert body["agent"]["tier"] == "plant"
        assert body["active_count"] == 1

        after = (await client.get("/agents")).json()["agents"]
        names_after = {a["name"] for a in after}
        assert "plant7-supplier-quality" in names_after
        assert len(after) == len(before) + 1

        reset = await client.post("/demo/hot-add/reset")
        assert reset.json() == {"cleared": 1}

        after_reset = (await client.get("/agents")).json()["agents"]
        assert {a["name"] for a in after_reset} == names_before


async def test_static_index_is_served():
    client, _ = await _async_client()
    async with client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    body = resp.text
    assert "MMC Demo" in body
    assert "EventSource" in body  # confirms the SSE client wiring is present
