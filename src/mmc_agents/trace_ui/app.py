"""FastAPI app for the Gate C trace UI.

Endpoints:
- ``POST /runs`` — start a scenario, returns ``run_id`` and SSE URL.
- ``GET  /runs/{run_id}/events`` — Server-Sent Events stream of ``TraceEvent``.
- ``GET  /agents`` — full 10-agent catalog with tier + project.
- ``GET  /agents/{name}/blast-radius`` — governance overlay (Task 7 fills this).
- ``POST /demo/hot-add`` — hot-add agent demo (Task 10 fills this).
- ``GET  /`` — static single-file demo UI.

Tests inject a ``ScenarioRunner`` so they never hit Foundry. The default
runner (``live_scenario_runner``) wires into ``run_stream`` against the real
orchestrator and is created lazily so importing this module is cheap.
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from mmc_agents.orchestrator.trace import TraceEvent
from mmc_agents.trace_ui.runtime import RunStore, ScenarioRunner
from mmc_agents.trace_ui.schemas import (
    AgentInfo,
    AgentListResponse,
    BlastRadiusResponse,
    CreateRunRequest,
    CreateRunResponse,
    HotAddRequest,
    HotAddResponse,
    ScenarioId,
)

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CATALOG_PATH = _REPO_ROOT / "agents" / "catalog.json"
_STATIC_DIR = Path(__file__).resolve().parent / "static"


def _load_agents() -> list[AgentInfo]:
    if not _CATALOG_PATH.exists():
        return []
    raw = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    out: list[AgentInfo] = []
    for entry in raw.get("agents", []):
        meta = entry.get("metadata", {}) or {}
        out.append(
            AgentInfo(
                name=entry.get("display_name") or entry.get("name", "(unnamed)"),
                tier=entry.get("tier", "plant"),
                description=entry.get("description") or entry.get("name", ""),
                foundry_project=meta.get("project"),
            )
        )
    return out


async def _live_scenario_runner(
    run_id: str, scenario: ScenarioId, task: str | None
) -> AsyncIterator[TraceEvent]:
    """Default runner wiring into ``run_stream`` against the live orchestrator.

    Imported lazily so the app can be instantiated for tests without pulling
    in azure-identity / agent_framework heavy modules.
    """
    from azure.identity import AzureCliCredential

    from mmc_agents.agent_factory import build_enterprise_agents, build_foundry_agents
    from mmc_agents.orchestrator.manager import _build_manager, run_stream
    from mmc_agents.orchestrator.scenarios.brake_caliper import TASK as BRAKE_TASK
    from mmc_agents.orchestrator.scenarios.loto_cluster import TASK as LOTO_TASK
    from agent_framework.orchestrations import MagenticBuilder
    import os

    scenario_task = task or (BRAKE_TASK if scenario == "brake_caliper" else LOTO_TASK)
    cred = AzureCliCredential()
    plant_endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    participants = build_foundry_agents("plant7", plant_endpoint, cred)
    ent_endpoint = os.environ.get("FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT")
    if ent_endpoint:
        participants = participants + build_enterprise_agents(ent_endpoint, cred)

    workflow = MagenticBuilder(participants=participants, manager=_build_manager()).build()
    async for event in run_stream(workflow, run_id=run_id, task=scenario_task):
        yield event


def create_app(runner: ScenarioRunner | None = None) -> FastAPI:
    """Create the FastAPI app. Pass ``runner`` to inject a fake for tests."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await app.state.store.shutdown()

    app = FastAPI(
        title="MMC Demo — Magentic Trace UI",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.store = RunStore(runner=runner or _live_scenario_runner)

    @app.get("/agents", response_model=AgentListResponse)
    async def list_agents() -> AgentListResponse:
        return AgentListResponse(agents=_load_agents())

    @app.get(
        "/agents/{name}/blast-radius",
        response_model=BlastRadiusResponse,
    )
    async def blast_radius(name: str) -> BlastRadiusResponse:
        # Task 7 fills this in. Placeholder keeps the contract stable.
        return BlastRadiusResponse(
            agent=name,
            available=False,
            detail="blast-radius overlay arrives in Gate C Task 7",
        )

    @app.post("/runs", response_model=CreateRunResponse)
    async def create_run(body: CreateRunRequest, request: Request) -> CreateRunResponse:
        session = app.state.store.create_run(body.scenario, body.task)
        events_url = str(request.url_for("stream_events", run_id=session.run_id))
        return CreateRunResponse(
            run_id=session.run_id,
            scenario=body.scenario,
            events_url=events_url,
        )

    @app.get("/runs/{run_id}/events", name="stream_events")
    async def stream_events(run_id: str, request: Request) -> EventSourceResponse:
        if app.state.store.get(run_id) is None:
            raise HTTPException(status_code=404, detail=f"run {run_id} not found")

        async def event_generator():
            async for event in app.state.store.subscribe(run_id):
                if await request.is_disconnected():
                    break
                yield {
                    "event": event.type,
                    "id": str(event.sequence),
                    "data": event.model_dump_json(),
                }

        return EventSourceResponse(event_generator())

    @app.post("/demo/hot-add", response_model=HotAddResponse)
    async def hot_add(body: HotAddRequest) -> HotAddResponse:
        # Task 10 fills this in.
        return HotAddResponse(
            accepted=False,
            detail="hot-add demo wiring arrives in Gate C Task 10",
        )

    if _STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

        @app.get("/", include_in_schema=False)
        async def index() -> FileResponse:
            return FileResponse(_STATIC_DIR / "index.html")

    return app
