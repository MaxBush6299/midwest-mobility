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
    HotAddResetResponse,
    HotAddResponse,
    ScenarioId,
    ScenarioInfo,
    ScenarioListResponse,
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
        tier = entry.get("tier", "plant")
        # Catalog only persists project for plant agents today; the enterprise
        # tier is single-tenant on mmc-enterprise, so infer when absent.
        project = meta.get("project") or ("mmc-enterprise" if tier == "enterprise" else None)
        # ``name`` is the catalog id (e.g. ``plant7-ehs``) — same string the
        # orchestrator emits as executor_id, so the UI can match exactly.
        # ``display_name`` is the human label shown in the left rail.
        catalog_name = entry.get("name") or "(unnamed)"
        out.append(
            AgentInfo(
                name=catalog_name,
                display_name=entry.get("display_name") or catalog_name,
                tier=tier,
                description=entry.get("description") or catalog_name,
                foundry_project=project,
            )
        )
    return out


# Pre-baked "shadow" agents the demo can pull onto the stage at runtime via
# POST /demo/hot-add. Storing them here (rather than reading from a file)
# keeps the demo's hot-add story self-contained — no filesystem mutation
# during the live run. Re-keyed by name for O(1) lookup.
_HOT_ADD_CATALOG: dict[str, AgentInfo] = {
    "plant7-supplier-quality": AgentInfo(
        name="plant7-supplier-quality",
        display_name="Plant 7 Supplier Quality (hot-added)",
        tier="plant",
        description=(
            "Cross-functional supplier-quality agent for incoming-material "
            "investigations. Demoed via hot-add at runtime — proves the "
            "registry tier picks up new agents without a redeploy."
        ),
        foundry_project="mmc-plant",
    ),
}


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
    from mmc_agents.orchestrator.scenarios.registry import get as get_scenario
    from agent_framework.orchestrations import MagenticBuilder
    import os

    spec = get_scenario(scenario)
    scenario_task = task or spec.problem_statement
    cred = AzureCliCredential()
    plant_endpoint = os.environ["FOUNDRY_PLANT_PROJECT_ENDPOINT"]
    participants = build_foundry_agents("plant7", plant_endpoint, cred)
    # Include plant4 if its profile is present (Gate D). plant4 agents live
    # in the mmc-plant4 Foundry project (canonical wiring per
    # scripts/generate_cards.py); fall back to the shared plant endpoint
    # if FOUNDRY_PLANT4_PROJECT_ENDPOINT isn't set.
    from pathlib import Path as _Path
    _repo_root = _Path(__file__).resolve().parents[3]
    if (_repo_root / "plants" / "plant4" / "profile.yaml").exists():
        plant4_endpoint = os.environ.get(
            "FOUNDRY_PLANT4_PROJECT_ENDPOINT", plant_endpoint
        )
        participants = participants + build_foundry_agents(
            "plant4", plant4_endpoint, cred
        )
    ent_endpoint = os.environ.get("FOUNDRY_ENTERPRISE_PROJECT_ENDPOINT")
    if ent_endpoint:
        participants = participants + build_enterprise_agents(ent_endpoint, cred)

    # Narrow scenarios scope the participant pool so the manager doesn't
    # plan against irrelevant agents. spec.participants is None for the
    # full 10-agent demos (brake_caliper / loto_cluster).
    if spec.participants:
        allowed = set(spec.participants)
        before = [getattr(p, "name", "?") for p in participants]
        participants = [p for p in participants if getattr(p, "name", None) in allowed]
        logger.info(
            "scenario %s scoped pool: %s -> %s (allowed=%s)",
            scenario, before, [getattr(p, "name", "?") for p in participants], sorted(allowed),
        )
        if not participants:
            raise RuntimeError(
                f"scenario {scenario!r} requested participants {sorted(allowed)} "
                f"but none matched available agent names {before}"
            )

    workflow = MagenticBuilder(
        participants=participants,
        manager=_build_manager(max_round_count=spec.max_rounds),
    ).build()
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
    # Names of hot-added agents that should appear in the next /agents response.
    # Stored on app.state so create_app() callers (including tests) start with
    # a clean slate and the lifespan teardown can clear it.
    app.state.hot_added: set[str] = set()

    @app.get("/agents", response_model=AgentListResponse)
    async def list_agents() -> AgentListResponse:
        agents = _load_agents()
        active_hot: list[AgentInfo] = []
        for name in sorted(app.state.hot_added):
            if name in _HOT_ADD_CATALOG:
                active_hot.append(_HOT_ADD_CATALOG[name])
        return AgentListResponse(agents=agents + active_hot)

    @app.get("/scenarios", response_model=ScenarioListResponse)
    async def list_scenarios() -> ScenarioListResponse:
        from mmc_agents.orchestrator.scenarios.registry import SCENARIOS

        return ScenarioListResponse(
            scenarios=[
                ScenarioInfo(
                    id=spec.id,  # type: ignore[arg-type]
                    label=spec.label,
                    blurb=spec.blurb,
                    problem_statement=spec.problem_statement,
                )
                for spec in SCENARIOS.values()
            ]
        )

    @app.get(
        "/agents/{name}/blast-radius",
        response_model=BlastRadiusResponse,
    )
    async def blast_radius(name: str) -> BlastRadiusResponse:
        from mmc_agents.governance.blast_radius import compute_blast_radius
        from mmc_agents.governance.metadata import (
            load_infra_metadata,
            load_kb_metadata,
        )

        try:
            kb_meta = load_kb_metadata()
            infra_meta = load_infra_metadata()
            br = compute_blast_radius(name, kb_meta, infra_meta)
        except KeyError:
            return BlastRadiusResponse(
                agent=name,
                available=False,
                detail=(
                    f"No governance metadata is mapped to agent {name!r}. "
                    "Hot-added agents must be re-baked into "
                    "governance/kb_metadata.json before the overlay can compute."
                ),
            )
        except FileNotFoundError as exc:
            return BlastRadiusResponse(
                agent=name,
                available=False,
                detail=f"Governance metadata missing on disk: {exc}",
            )

        return BlastRadiusResponse(
            agent=br.agent,
            available=True,
            foundry_project=br.foundry_project,
            knowledge_base=br.knowledge_base,
            summary=br.summary,
            edges=[e.model_dump() for e in br.edges],
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
        existing = {a.name for a in _load_agents()}
        if body.name in existing:
            return HotAddResponse(
                accepted=False,
                detail=f"agent {body.name!r} is already in the persisted catalog",
                active_count=len(app.state.hot_added),
            )
        # The demo only allows hot-adding from the pre-baked shadow catalog so
        # an attacker can't conjure arbitrary executor IDs into the trace.
        if body.name not in _HOT_ADD_CATALOG:
            return HotAddResponse(
                accepted=False,
                detail=(
                    f"agent {body.name!r} is not in the demo hot-add catalog "
                    f"({sorted(_HOT_ADD_CATALOG)}). Add it to _HOT_ADD_CATALOG "
                    "in src/mmc_agents/trace_ui/app.py first."
                ),
                active_count=len(app.state.hot_added),
            )
        app.state.hot_added.add(body.name)
        return HotAddResponse(
            accepted=True,
            agent=_HOT_ADD_CATALOG[body.name],
            detail=(
                f"agent {body.name!r} added to the in-memory catalog. The next "
                "/agents request will include it; rerun a scenario to give the "
                "manager a chance to dispatch to it."
            ),
            active_count=len(app.state.hot_added),
        )

    @app.post("/demo/hot-add/reset", response_model=HotAddResetResponse)
    async def hot_add_reset() -> HotAddResetResponse:
        cleared = len(app.state.hot_added)
        app.state.hot_added = set()
        return HotAddResetResponse(cleared=cleared)

    if _STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

        @app.get("/", include_in_schema=False)
        async def index() -> FileResponse:
            return FileResponse(_STATIC_DIR / "index.html")

    return app
