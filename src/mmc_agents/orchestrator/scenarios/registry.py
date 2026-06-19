"""Scenario registry — single source of truth for the orchestrator and UI.

Each scenario module exports ``PROBLEM_STATEMENT`` and ``EXPECTED_BOUNDS``.
The registry maps the scenario id (used by the HTTP API and tests) to its
problem statement and a short blurb for the UI.

Adding a new scenario is a 2-line change: drop a module in this package,
add an entry to ``SCENARIOS`` below.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import (
    brake_caliper,
    loto_cluster,
    multi_plant_warranty,
    pm_check,
    po_status,
    supplier_risk_pm,
    training_gap,
)


@dataclass(frozen=True)
class ScenarioSpec:
    id: str
    label: str
    blurb: str  # HTML-safe, may contain <code> tags
    problem_statement: str
    # When None, the manager sees the full 10-agent roster. When a tuple,
    # only those agents are wired into MagenticBuilder participants — keeps
    # narrow scenarios tightly scoped and the plan focused.
    participants: tuple[str, ...] | None = None
    # Per-scenario manager cap. Narrow scenarios should converge in 2-3
    # rounds; the full brake-caliper run needs the default 15.
    max_rounds: int = 15


SCENARIOS: dict[str, ScenarioSpec] = {
    "brake_caliper": ScenarioSpec(
        id="brake_caliper",
        label="Brake caliper · NO_DIRECT_ALT",
        blurb=(
            "A Plant 7 line stop on <code>BRK-CAL-XYZ</code>. The plant "
            "supplier-quality agent observes <code>NO_DIRECT_ALT</code>, "
            "prompting the manager to fan out to enterprise procurement, "
            "PLM, and demand to find a mitigation. <em>~30 hops, all 10 agents.</em>"
        ),
        problem_statement=brake_caliper.PROBLEM_STATEMENT,
    ),
    "loto_cluster": ScenarioSpec(
        id="loto_cluster",
        label="LOTO cluster · L1 Press near-misses",
        blurb=(
            "Three L1 Press near-misses in 60 days "
            "(<code>INC-062/063/064</code>) with open CAPAs. EHS, "
            "maintenance, training, and quality collaborate; enterprise "
            "quality verifies the CAPA cluster. <em>~15 hops, 5-6 agents.</em>"
        ),
        problem_statement=loto_cluster.PROBLEM_STATEMENT,
    ),
    "multi_plant_warranty": ScenarioSpec(
        id="multi_plant_warranty",
        label="Multi-plant warranty · BRK-CAL-XYZ spike",
        blurb=(
            "Cross-plant warranty spike on <code>BRK-CAL-XYZ</code>. Plant 7 "
            "and Plant 4 quality + maintenance respond locally while "
            "<em>ent-quality</em> and <em>ent-supply-chain</em> coordinate "
            "with <em>Acme Brakes</em>. <em>~60 hops, all plant + enterprise agents.</em>"
        ),
        problem_statement=multi_plant_warranty.PROBLEM_STATEMENT,
    ),
    "training_gap": ScenarioSpec(
        id="training_gap",
        label="LOTO refresher · expirations",
        blurb=(
            "Plant-only check grounded in <code>MMC_P7_Training_Log.csv</code>: "
            "list every Plant 7 employee whose <em>LOTO Authorized Person</em> "
            "training expires before 2026-12-31. <em>~3-5 hops, 1 agent "
            "(training).</em>"
        ),
        problem_statement=training_gap.PROBLEM_STATEMENT,
        participants=("plant7-training",),
        max_rounds=5,
    ),
    "po_status": ScenarioSpec(
        id="po_status",
        label="At-risk POs · SUP-001",
        blurb=(
            "Enterprise-only check grounded in <code>po_spend.csv</code>: open "
            "POs with Acme Brakes flagged <em>At Risk</em> or <em>Watch</em>. "
            "<em>~3-5 hops, 1 agent (procurement).</em>"
        ),
        problem_statement=po_status.PROBLEM_STATEMENT,
        participants=("ent-procurement",),
        max_rounds=5,
    ),
    "pm_check": ScenarioSpec(
        id="pm_check",
        label="Line 1 PM · follow-up WOs",
        blurb=(
            "Plant-only check grounded in <code>MMC_P7_PM_Schedule.csv</code>: "
            "Line 1 PM tasks that generated follow-up work orders this quarter. "
            "<em>~3-5 hops, 1 agent (quality — owns the logs KB).</em>"
        ),
        problem_statement=pm_check.PROBLEM_STATEMENT,
        participants=("plant7-quality",),
        max_rounds=5,
    ),
    "supplier_risk_pm": ScenarioSpec(
        id="supplier_risk_pm",
        label="At-risk PO · PM impact + alt supplier",
        blurb=(
            "Cross-KB SQL story: <code>PO-00001</code> (BRK-CAL-XYZ, SUP-001) "
            "is At Risk. Procurement confirms the PO row, plant maintenance "
            "finds Line 1 PMs touching the part, and supply chain checks "
            "<code>supplier_master</code> for a backup. "
            "<em>~6-10 hops, 3 agents.</em>"
        ),
        problem_statement=supplier_risk_pm.PROBLEM_STATEMENT,
        participants=(
            "ent-procurement",
            "plant7-maintenance",
            "ent-supply-chain",
        ),
        max_rounds=8,
    ),
}


def get(scenario_id: str) -> ScenarioSpec:
    if scenario_id not in SCENARIOS:
        raise KeyError(f"unknown scenario {scenario_id!r}; have {list(SCENARIOS)}")
    return SCENARIOS[scenario_id]
