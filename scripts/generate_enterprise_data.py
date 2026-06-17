"""Deterministic enterprise CSV generator (Gate B Task 4).

Reads `enterprise/scenario_seed.yaml` and emits per-node CSVs into
`enterprise/<node>/data/`. Output is fully deterministic — same seed +
same node spec yields byte-identical CSVs.

CLI: `python -m scripts.generate_enterprise_data [node ...]`
     (defaults to all nodes)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]

NODE_SPECS: dict[str, list[str]] = {
    "supply-chain": [
        "supplier_master.csv",
        "bom_where_used.csv",
        "erp_inventory.csv",
        "tms_freight.csv",
    ],
    "procurement": ["contracts.csv", "po_spend.csv", "should_cost_model.csv"],
    "engineering-plm": ["plm_part_master.csv", "eco_log.csv", "effectivity.csv"],
    "enterprise-quality": [
        "warranty_claims.csv",
        "field_failure_feed.csv",
        "recall_ruleset.csv",
    ],
    "demand-program": [
        "order_crm_feed.csv",
        "program_plan.csv",
        "allocation_model.csv",
    ],
}

# Anchored supporting parts/suppliers used across nodes (deterministic).
_SUPPLIERS = [
    ("SUP-001", "Acme Brakes", 1, "US", 14, "Y", 21, "High"),
    ("SUP-002", "Midwest Stampings", 2, "US", 7, "N", 0, "Low"),
    ("SUP-003", "Globex Robotics", 1, "DE", 28, "N", 0, "Medium"),
    ("SUP-004", "Initech Fasteners", 2, "US", 5, "N", 0, "Low"),
    ("SUP-005", "Hooli Castings", 1, "MX", 21, "N", 0, "Medium"),
    ("SUP-006", "Pied Piper Polymers", 2, "US", 10, "N", 0, "Low"),
    ("SUP-007", "Soylent Steel", 1, "US", 18, "N", 0, "Medium"),
    ("SUP-008", "Massive Dynamic Wire", 2, "JP", 35, "N", 0, "Medium"),
    ("SUP-009", "Cyberdyne Sensors", 1, "US", 12, "N", 0, "Low"),
    ("SUP-010", "Tyrell Optics", 2, "US", 22, "N", 0, "Medium"),
    ("SUP-011", "Aperture Fluids", 2, "US", 8, "N", 0, "Low"),
    ("SUP-012", "Wayne Forgings", 1, "US", 19, "N", 0, "Medium"),
    ("SUP-013", "Stark Composites", 1, "US", 25, "N", 0, "Medium"),
    ("SUP-014", "Oscorp Adhesives", 2, "US", 11, "N", 0, "Low"),
    ("SUP-015", "Umbrella Coatings", 2, "DE", 30, "N", 0, "Medium"),
    ("SUP-016", "Nakatomi Electronics", 1, "JP", 32, "N", 0, "Medium"),
    ("SUP-017", "Vandelay Plastics", 2, "US", 9, "N", 0, "Low"),
    ("SUP-018", "Wonka Lubricants", 2, "US", 6, "N", 0, "Low"),
    ("SUP-019", "Hanso Hydraulics", 1, "KR", 27, "N", 0, "Medium"),
    ("SUP-020", "Spacely Springs", 2, "US", 8, "N", 0, "Low"),
    ("SUP-021", "Cogswell Cogs", 2, "US", 9, "N", 0, "Low"),
    ("SUP-022", "Tessier-Ashpool Bearings", 1, "JP", 30, "N", 0, "Medium"),
    ("SUP-023", "Yutani Castings", 1, "MX", 20, "N", 0, "Medium"),
    ("SUP-024", "MomCorp Servos", 1, "US", 15, "N", 0, "Medium"),
    ("SUP-025", "Buy n Large Boards", 2, "CN", 40, "N", 0, "High"),
    ("SUP-026", "Encom Firmware", 2, "US", 14, "N", 0, "Low"),
    ("SUP-027", "Rekall Memory", 1, "US", 16, "N", 0, "Medium"),
    ("SUP-028", "Veridian Dynamics Trim", 2, "US", 7, "N", 0, "Low"),
]

# (Part_ID, Name, Supplier_ID, Plant_ID, Line_ID, Qty, Effective_Date)
_PARTS = [
    ("BRK-CAL-XYZ", "Brake Caliper Assembly", "SUP-001", "plant7", "L1", 1, "2025-01-01"),
    ("STM-PNL-A1", "Stamped Panel A1", "SUP-002", "plant7", "L1", 2, "2025-01-01"),
    ("ROB-ARM-G3", "Robot Arm Gen3", "SUP-003", "plant7", "L2", 1, "2025-01-01"),
    ("FST-M8-100", "M8 Fastener Pack", "SUP-004", "plant7", "L1", 50, "2025-01-01"),
    ("CST-HSG-04", "Cast Housing 04", "SUP-005", "plant7", "L3", 1, "2025-01-01"),
    ("BRK-PAD-STD", "Brake Pad Standard", "SUP-001", "plant7", "L1", 4, "2025-01-01"),
    ("BRK-ROT-090", "Brake Rotor 090mm", "SUP-007", "plant7", "L1", 1, "2025-01-01"),
    ("ELC-HRN-12V", "12V Wiring Harness", "SUP-008", "plant7", "L2", 1, "2025-01-01"),
    ("SNS-PRX-001", "Proximity Sensor 001", "SUP-009", "plant7", "L2", 2, "2025-01-01"),
    ("OPT-LNS-002", "Optical Lens 002", "SUP-010", "plant7", "L3", 1, "2025-01-01"),
]


def _write_csv(path: Path, header: list[str], rows: list[list[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


# --- supply-chain ---------------------------------------------------------

def _gen_supply_chain(out: Path, seed: dict) -> None:
    _write_csv(
        out / "supplier_master.csv",
        ["Supplier_ID", "Name", "Tier", "Country", "Lead_Time_Days",
         "Disruption_Flag", "Disruption_Days", "Risk_Score"],
        [list(s) for s in _SUPPLIERS],
    )
    _write_csv(
        out / "bom_where_used.csv",
        ["Part_ID", "Part_Name", "Supplier_ID", "Plant_ID", "Line_ID",
         "Qty_Per_Assy", "Effective_Date"],
        [list(p) for p in _PARTS],
    )
    rows = []
    for p in _PARTS:
        part_id, _, supplier_id, plant_id, line_id, qty, _ = p
        on_hand = (hash(part_id) % 400) + 50
        rows.append([part_id, plant_id, line_id, on_hand, qty * 10, supplier_id])
    _write_csv(
        out / "erp_inventory.csv",
        ["Part_ID", "Plant_ID", "Line_ID", "On_Hand_Qty", "Reorder_Point", "Supplier_ID"],
        rows,
    )
    freight_rows = []
    modes = ["Truck", "Rail", "Ocean", "Air"]
    for i, s in enumerate(_SUPPLIERS):
        sid, _name, _tier, country, lead, *_ = s
        mode = modes[i % len(modes)]
        cost = lead * 27 + (hash(sid) % 500)
        freight_rows.append([f"FRT-{i+1:03d}", sid, country, "plant7", mode, lead, cost])
    _write_csv(
        out / "tms_freight.csv",
        ["Freight_ID", "Supplier_ID", "Origin_Country", "Dest_Plant_ID",
         "Mode", "Transit_Days", "Cost_USD"],
        freight_rows,
    )


# --- procurement ----------------------------------------------------------

def _gen_procurement(out: Path, seed: dict) -> None:
    contracts = []
    for i, p in enumerate(_PARTS):
        part_id, _, supplier_id, *_ = p
        contracts.append([
            f"CON-{i+1:03d}", supplier_id, part_id,
            "2025-01-01", "2026-12-31",
            round(50 + (hash(part_id) % 200) * 0.5, 2),
            "USD", "Active",
        ])
    _write_csv(
        out / "contracts.csv",
        ["Contract_ID", "Supplier_ID", "Part_ID", "Start_Date", "End_Date",
         "Unit_Price", "Currency", "Status"],
        contracts,
    )
    po = []
    for i, p in enumerate(_PARTS):
        part_id, _, supplier_id, plant_id, *_ = p
        qty = ((hash(part_id) % 90) + 10) * 5
        unit = round(50 + (hash(part_id) % 200) * 0.5, 2)
        po.append([
            f"PO-{i+1:04d}", supplier_id, part_id, qty, unit,
            round(qty * unit, 2), "2026-03-15", plant_id,
        ])
    _write_csv(
        out / "po_spend.csv",
        ["PO_ID", "Supplier_ID", "Part_ID", "Qty", "Unit_Price", "Total",
         "Order_Date", "Plant_ID"],
        po,
    )
    sc = []
    for p in _PARTS:
        part_id = p[0]
        mat = round(20 + (hash(part_id) % 80) * 0.4, 2)
        labor = round(10 + (hash(part_id + "L") % 30) * 0.5, 2)
        oh = round(labor * 0.6, 2)
        log = round((hash(part_id + "F") % 40) * 0.25, 2)
        sc.append([part_id, mat, labor, oh, log, round(mat + labor + oh + log, 2)])
    _write_csv(
        out / "should_cost_model.csv",
        ["Part_ID", "Material_Cost", "Labor_Cost", "Overhead", "Logistics", "Target_Price"],
        sc,
    )


# --- engineering-plm ------------------------------------------------------

def _gen_engineering_plm(out: Path, seed: dict) -> None:
    pm = []
    families = {"BRK": "Brake", "STM": "Stamping", "ROB": "Robotics",
                "FST": "Fastener", "CST": "Casting", "ELC": "Electrical",
                "SNS": "Sensor", "OPT": "Optical"}
    for p in _PARTS:
        part_id, name, supplier_id, *_ = p
        fam = families.get(part_id[:3], "General")
        pm.append([part_id, name, "A", "Released", supplier_id, fam])
    _write_csv(
        out / "plm_part_master.csv",
        ["Part_ID", "Description", "Rev", "Status", "Owner_Supplier_ID", "Family"],
        pm,
    )
    eco = []
    for i, p in enumerate(_PARTS):
        part_id = p[0]
        eco.append([
            f"ECO-{i+1:04d}", part_id, "A", "B",
            "Material change for cost reduction" if i % 2 == 0 else "Tolerance tightening",
            "2026-02-10", "engineering-plm",
        ])
    _write_csv(
        out / "eco_log.csv",
        ["ECO_ID", "Part_ID", "From_Rev", "To_Rev", "Reason", "Date", "Approver"],
        eco,
    )
    eff = []
    for p in _PARTS:
        part_id, _, _, plant_id, line_id, *_ = p
        eff.append([part_id, plant_id, line_id, "2025-01-01", "2027-12-31"])
    _write_csv(
        out / "effectivity.csv",
        ["Part_ID", "Plant_ID", "Line_ID", "Effective_From", "Effective_To"],
        eff,
    )


# --- enterprise-quality ---------------------------------------------------

def _gen_enterprise_quality(out: Path, seed: dict) -> None:
    bc_part = seed["brake_caliper"]["part_id"]
    modes = ["Seal Leak", "Caliper Drag", "Pad Wear", "Rotor Warp", "Sensor Fault"]
    claims = []
    for i in range(30):
        part_id = bc_part if i % 4 == 0 else _PARTS[i % len(_PARTS)][0]
        mode = modes[i % len(modes)]
        cost = 120 + (hash(part_id + str(i)) % 400)
        claims.append([
            f"WC-{i+1:04d}", part_id, "plant7",
            f"2026-{(i % 6) + 1:02d}-{(i % 27) + 1:02d}",
            mode, cost, f"VIN{(hash(part_id + str(i)) % 999999):06d}",
        ])
    _write_csv(
        out / "warranty_claims.csv",
        ["Claim_ID", "Part_ID", "Plant_ID", "Date", "Failure_Mode",
         "Cost_USD", "VIN_Hash"],
        claims,
    )
    feed = []
    regions = ["NA", "EU", "APAC", "LATAM"]
    severities = ["Low", "Medium", "High"]
    for i in range(24):
        part_id = bc_part if i % 5 == 0 else _PARTS[i % len(_PARTS)][0]
        feed.append([
            f"FF-{i+1:04d}", part_id,
            f"2026-{(i % 6) + 1:02d}-{(i % 27) + 1:02d}",
            regions[i % len(regions)],
            (hash(part_id + str(i)) % 18) + 1,
            severities[i % len(severities)],
        ])
    _write_csv(
        out / "field_failure_feed.csv",
        ["Feed_ID", "Part_ID", "Date", "Region", "Count", "Severity"],
        feed,
    )
    _write_csv(
        out / "recall_ruleset.csv",
        ["Rule_ID", "Threshold_Type", "Threshold_Value", "Action"],
        [
            ["RR-001", "claims_per_1k_in_90d", 5, "Open investigation"],
            ["RR-002", "field_high_severity_in_30d", 10, "Recall candidate review"],
            ["RR-003", "cost_per_part_in_180d_usd", 50000, "Engineering escalation"],
        ],
    )


# --- demand-program -------------------------------------------------------

def _gen_demand_program(out: Path, seed: dict) -> None:
    programs = [
        ("PROG-EV1", "EV Platform 1", "BigOEM", "2026-01-01", "2027-06-30", 120000),
        ("PROG-LD7", "Light Duty 7", "MidOEM", "2026-03-01", "2027-09-30", 80000),
        ("PROG-CV3", "Commercial Van 3", "Heavy Inc", "2026-02-15", "2027-08-31", 45000),
    ]
    _write_csv(
        out / "program_plan.csv",
        ["Program_ID", "Name", "Customer", "Start_Date", "End_Date", "Volume_Annual"],
        [list(p) for p in programs],
    )
    orders = []
    for i, p in enumerate(_PARTS):
        part_id, _, _, plant_id, *_ = p
        program = programs[i % len(programs)][0]
        customer = programs[i % len(programs)][2]
        qty = ((hash(part_id + program) % 90) + 10) * 100
        orders.append([
            f"ORD-{i+1:05d}", customer, part_id, qty,
            f"2026-{(i % 6) + 4:02d}-{(i % 27) + 1:02d}", program,
        ])
    _write_csv(
        out / "order_crm_feed.csv",
        ["Order_ID", "Customer", "Part_ID", "Qty", "Need_Date", "Program_ID"],
        orders,
    )
    alloc = []
    for p in _PARTS:
        part_id, _, _, plant_id, line_id, *_ = p
        alloc.append([part_id, plant_id, line_id, 100])
    _write_csv(
        out / "allocation_model.csv",
        ["Part_ID", "Plant_ID", "Line_ID", "Allocated_Pct"],
        alloc,
    )


_GENERATORS = {
    "supply-chain": _gen_supply_chain,
    "procurement": _gen_procurement,
    "engineering-plm": _gen_engineering_plm,
    "enterprise-quality": _gen_enterprise_quality,
    "demand-program": _gen_demand_program,
}


def generate_node(node: str, out_dir: Path, seed: dict) -> None:
    if node not in _GENERATORS:
        raise ValueError(f"Unknown node: {node!r}. Valid: {sorted(_GENERATORS)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    _GENERATORS[node](out_dir, seed)


def main(argv: list[str]) -> int:
    seed = yaml.safe_load((ROOT / "enterprise" / "scenario_seed.yaml").read_text(encoding="utf-8"))
    nodes = argv or list(NODE_SPECS)
    for node in nodes:
        out_dir = ROOT / "enterprise" / node / "data"
        generate_node(node, out_dir, seed)
        print(f"generated {node} -> {out_dir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
