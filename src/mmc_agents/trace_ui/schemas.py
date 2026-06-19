"""Request / response schemas for the trace UI HTTP surface."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ScenarioId = Literal[
    "brake_caliper",
    "loto_cluster",
    "training_gap",
    "po_status",
    "pm_check",
    "supplier_risk_pm",
    "multi_plant_warranty",
    "multi_plant_training",
]
Tier = Literal["plant", "enterprise"]


class CreateRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario: ScenarioId = Field(
        description="Which built-in scenario to run. Each scenario seeds its own task."
    )
    task: str | None = Field(
        default=None,
        description=(
            "Optional override for the scenario's default task statement. "
            "Most demos use the default so the trace matches the run-of-show."
        ),
    )


class CreateRunResponse(BaseModel):
    run_id: str
    scenario: ScenarioId
    events_url: str


class ScenarioInfo(BaseModel):
    id: ScenarioId
    label: str
    blurb: str
    problem_statement: str


class ScenarioListResponse(BaseModel):
    scenarios: list[ScenarioInfo]


class AgentInfo(BaseModel):
    name: str
    display_name: str | None = None
    tier: Tier
    description: str
    foundry_project: str | None = None


class AgentListResponse(BaseModel):
    agents: list[AgentInfo]


class BlastRadiusEdgeInfo(BaseModel):
    kind: str
    target: str
    detail: str
    revocation_effect: str


class BlastRadiusResponse(BaseModel):
    """Per-agent governance overlay.

    ``available=False`` is returned when the agent is unknown to the
    governance metadata (e.g. it was hot-added at runtime and hasn't been
    re-baked into ``per_agent_readable_sources`` yet) — the UI uses that to
    render a graceful "no governance data" state instead of erroring."""

    agent: str
    available: bool
    foundry_project: str | None = None
    knowledge_base: str | None = None
    summary: str | None = None
    edges: list[BlastRadiusEdgeInfo] = Field(default_factory=list)
    detail: str | None = None


class HotAddRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    tier: Tier = "plant"
    display_name: str | None = None
    description: str | None = None
    foundry_project: str | None = None


class HotAddResponse(BaseModel):
    accepted: bool
    agent: AgentInfo | None = None
    detail: str | None = None
    active_count: int | None = None


class HotAddResetResponse(BaseModel):
    cleared: int
