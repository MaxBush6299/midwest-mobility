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


class BlastRadiusResponse(BaseModel):
    """Placeholder; Task 7 fills this in with computed scope data."""

    agent: str
    available: bool
    detail: str | None = None


class HotAddRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    tier: Tier = "plant"


class HotAddResponse(BaseModel):
    accepted: bool
    agent: AgentInfo | None = None
    detail: str | None = None
