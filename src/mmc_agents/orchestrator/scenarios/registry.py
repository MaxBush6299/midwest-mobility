"""Scenario registry — single source of truth for the orchestrator and UI.

Each scenario module exports ``PROBLEM_STATEMENT`` and ``EXPECTED_BOUNDS``.
The registry maps the scenario id (used by the HTTP API and tests) to its
problem statement and a short blurb for the UI.

Adding a new scenario is a 2-line change: drop a module in this package,
add an entry to ``SCENARIOS`` below.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import brake_caliper, loto_cluster, pm_check, po_status, training_gap


@dataclass(frozen=True)
class ScenarioSpec:
    id: str
    label: str
    blurb: str  # HTML-safe, may contain <code> tags
    problem_statement: str


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
    "training_gap": ScenarioSpec(
        id="training_gap",
        label="Training gap · LOTO refresher",
        blurb=(
            "Quick plant-only check: who's due for a LOTO refresher this "
            "quarter, and are they on shift? <em>~4-6 hops, 2 agents "
            "(training + EHS).</em>"
        ),
        problem_statement=training_gap.PROBLEM_STATEMENT,
    ),
    "po_status": ScenarioSpec(
        id="po_status",
        label="PO status · SUP-001 inbound",
        blurb=(
            "Enterprise-only: open POs with Acme Brakes and inbound "
            "shipment status. <em>~4-6 hops, 2 agents "
            "(procurement + supply-chain).</em>"
        ),
        problem_statement=po_status.PROBLEM_STATEMENT,
    ),
    "pm_check": ScenarioSpec(
        id="pm_check",
        label="PM check · L1 Press window",
        blurb=(
            "Smallest scenario: is L1 Press due for PM in 7 days, and "
            "which shift can take the downtime? <em>~4 hops, 2 agents "
            "(maintenance + shift-ops).</em>"
        ),
        problem_statement=pm_check.PROBLEM_STATEMENT,
    ),
}


def get(scenario_id: str) -> ScenarioSpec:
    if scenario_id not in SCENARIOS:
        raise KeyError(f"unknown scenario {scenario_id!r}; have {list(SCENARIOS)}")
    return SCENARIOS[scenario_id]
