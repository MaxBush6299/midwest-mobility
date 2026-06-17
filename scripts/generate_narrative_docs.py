"""Deterministic narrative doc generator (Gate B Task 5).

For each enterprise node, renders a small set of policy/procedure markdown
docs that pass `scripts.validate_naming`. The output deliberately weaves in
the brake-caliper cross-link facts from `enterprise/scenario_seed.yaml` so
the narrative docs reinforce the CSV cross-links.

The default `render_doc()` is a pure deterministic template — no LLM call.
An LLM-mode hook is intentionally left out at Gate B; GitHub Copilot is the
operator-side LLM for this repo and emits markdown directly when needed.

CLI: `python -m scripts.generate_narrative_docs [node ...]`
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
_SEED_PATH = ROOT / "enterprise" / "scenario_seed.yaml"

DOCS: dict[str, list[str]] = {
    "supply-chain": [
        "supplier_qualification_policy.md",
        "logistics_sop.md",
        "disruption_playbook.md",
    ],
    "procurement": [
        "procurement_policy.md",
        "expedite_cost_methodology.md",
        "supplier_tier_definitions.md",
    ],
    "engineering-plm": [
        "eco_workflow.md",
        "part_numbering_standard.md",
        "cross_plant_change_procedure.md",
    ],
    "enterprise-quality": [
        "warranty_handling_sop.md",
        "recall_threshold_policy.md",
        "cross_plant_defect_trend_methodology.md",
    ],
    "demand-program": [
        "launch_readiness_checklist.md",
        "demand_allocation_policy.md",
        "oem_program_definitions.md",
    ],
}


def _load_seed() -> dict:
    return yaml.safe_load(_SEED_PATH.read_text(encoding="utf-8"))


_BODY_TEMPLATES: dict[str, str] = {
    "supplier_qualification_policy.md": (
        "All suppliers feeding {plant_code} {line_id} must complete the MMC "
        "qualification program before producing {part_id} ({part_name}). "
        "{supplier_name} ({supplier_id}) is the incumbent supplier of record."
    ),
    "logistics_sop.md": (
        "Inbound freight to {plant_code} {line_id} for {part_id} follows the "
        "primary truck lane from {supplier_name} ({supplier_id}). Customs and "
        "lane substitution rules are tracked in tms_freight.csv."
    ),
    "disruption_playbook.md": (
        "If {supplier_name} ({supplier_id}) signals a disruption on {part_id}, "
        "expect a {disruption_days}-day impact on {plant_code} {line_id}. "
        "Trigger supplier.alternates(); if no alternate, escalate to procurement."
    ),
    "procurement_policy.md": (
        "Procurement contracts for {part_id} are negotiated by category managers "
        "covering {plant_code} {line_id}. Standards: OSHA 29 CFR 1910, ISO 9001."
    ),
    "expedite_cost_methodology.md": (
        "Expedite cost for {part_id} at {plant_code} {line_id} is computed as "
        "freight delta plus premium labor. See should_cost_model.csv."
    ),
    "supplier_tier_definitions.md": (
        "Tier 1 suppliers (e.g., {supplier_name} {supplier_id}) ship directly to "
        "{plant_code} {line_id}. Tier 2 supplies feed Tier 1."
    ),
    "eco_workflow.md": (
        "Engineering change orders for {part_id} ({part_name}) require sign-off "
        "from {plant_code} {line_id} engineering and quality before release. "
        "Standards: ISO 9001."
    ),
    "part_numbering_standard.md": (
        "Part IDs use the XXX-XXXX-XXXX format. Example: {part_id}. Equipment IDs "
        "use L1-PRS-001 style for {plant_code} {line_id} press lines."
    ),
    "cross_plant_change_procedure.md": (
        "Cross-plant changes affecting {part_id} must be validated against "
        "{plant_code} effectivity before release on any other plant."
    ),
    "warranty_handling_sop.md": (
        "Warranty claims on {part_id} from {plant_code} {line_id} are logged in "
        "warranty_claims.csv and reviewed weekly. Standards: ISO 9001."
    ),
    "recall_threshold_policy.md": (
        "Recall candidacy for {part_id} is triggered when warranty/field metrics "
        "exceed the rules in recall_ruleset.csv. {plant_code} {line_id} is the "
        "primary production source."
    ),
    "cross_plant_defect_trend_methodology.md": (
        "Defect trends on {part_id} are normalized per 1,000 units shipped. "
        "{plant_code} {line_id} baselines anchor the network comparison."
    ),
    "launch_readiness_checklist.md": (
        "Launch readiness for {part_id} requires {plant_code} {line_id} PPAP "
        "approval, capacity confirmation, and supplier readiness from {supplier_name} "
        "({supplier_id})."
    ),
    "demand_allocation_policy.md": (
        "Demand for {part_id} is allocated 100% to {plant_code} {line_id} unless "
        "the allocation_model.csv routes otherwise."
    ),
    "oem_program_definitions.md": (
        "OEM programs consume {part_id} from {plant_code} {line_id}. See "
        "program_plan.csv for the active program list."
    ),
}


def render_doc(node: str, filename: str, seed: dict | None = None) -> str:
    if node not in DOCS:
        raise ValueError(f"Unknown node: {node!r}")
    if filename not in DOCS[node]:
        raise ValueError(f"{filename!r} is not registered for node {node!r}")
    seed = seed or _load_seed()
    bc = seed["brake_caliper"]
    ctx = {
        "plant_code": bc["plant_code"],
        "line_id": bc["line_id"],
        "part_id": bc["part_id"],
        "part_name": bc["part_name"],
        "supplier_id": bc["supplier_id"],
        "supplier_name": bc["supplier_name"],
        "disruption_days": bc["disruption_days"],
    }
    body = _BODY_TEMPLATES[filename].format(**ctx)
    title = filename.replace(".md", "").replace("_", " ").title()
    return f"# {title}\n\n{body}\n"


def main(argv: list[str]) -> int:
    seed = _load_seed()
    nodes = argv or list(DOCS)
    for node in nodes:
        out_dir = ROOT / "enterprise" / node / "kb"
        out_dir.mkdir(parents=True, exist_ok=True)
        for filename in DOCS[node]:
            text = render_doc(node, filename, seed)
            (out_dir / filename).write_text(text, encoding="utf-8")
        print(f"rendered {node} -> {out_dir.relative_to(ROOT)} ({len(DOCS[node])} docs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
