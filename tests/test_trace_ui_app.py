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
    assert len(names) == 10, f"expected 10 agents, got {len(names)}: {names}"
    assert tiers == {"plant", "enterprise"}


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


async def test_blast_radius_placeholder_response():
    client, _ = await _async_client()
    async with client:
        resp = await client.get("/agents/p7-supplier-quality/blast-radius")
    assert resp.status_code == 200
    body = resp.json()
    assert body["agent"] == "p7-supplier-quality"
    assert body["available"] is False


async def test_hot_add_placeholder_response():
    client, _ = await _async_client()
    async with client:
        resp = await client.post(
            "/demo/hot-add", json={"name": "plant7-external-auditor"}
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["accepted"] is False
    assert "Task 10" in body["detail"]
