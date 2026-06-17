"""Deterministic enterprise CSV generator (Gate B Tasks 4 + 6-10).

Reads `enterprise/scenario_seed.yaml` and emits per-node CSVs into
`enterprise/<node>/data/`. Output is fully deterministic — same seed +
same node spec yields byte-identical CSVs.

Schemas follow the plan in
`docs/plans/2026-06-16-gate-b-full-network.md` Tasks 6-10.

CLI: `python -m scripts.generate_enterprise_data [--node NAME ...]`
     (defaults to all nodes)
"""
from __future__ import annotations

import argparse
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

PROGRAM_CODES = {
    "BRK": "EV-BRK-26",
    "STM": "MMC-BODY-25",
    "ROB": "MMC-AUTO-24",
    "FST": "MMC-GEN",
    "CST": "MMC-CAST-25",
    "ELC": "MMC-AUTO-24",
    "SNS": "MMC-AUTO-24",
    "OPT": "MMC-AUTO-24",
}

# (Supplier_ID, Supplier_Name, Tier, Country, Primary_Commodity,
#  Qualification_Status, Lead_Time_Days, Disruption_Flag, Disruption_Days,
#  Risk_Score, Preferred_Alt_Supplier_ID, Notes)
_SUPPLIERS: list[tuple[Any, ...]] = [
    ("SUP-001", "Acme Brakes", 1, "US", "Brake Systems", "Critical", 14, "Y", 21, "High", "", "NO_DIRECT_ALT for BRK-CAL-XYZ; manager must backtrack to procurement/PLM/demand"),
    ("SUP-002", "Midwest Stampings", 2, "US", "Stamped Components", "Approved", 10, "N", 0, "Low", "SUP-006", "Approved backup for L1 stampings"),
    ("SUP-003", "Globex Robotics", 1, "DE", "Robotics", "Approved", 28, "N", 0, "Medium", "SUP-008", "L2 robot-cell components"),
    ("SUP-004", "Initech Fasteners", 2, "US", "Fasteners", "Approved", 7, "N", 0, "Low", "SUP-009", "Common M8/M10 packs"),
    ("SUP-005", "Hooli Castings", 1, "MX", "Castings", "Approved", 21, "N", 0, "Medium", "SUP-010", "General cast housings"),
    ("SUP-006", "Pied Piper Polymers", 2, "US", "Polymer Components", "Approved", 12, "N", 0, "Low", "SUP-002", "Alternate stamping/polymer"),
    ("SUP-007", "Soylent Steel", 1, "US", "Brake Components", "Approved", 18, "N", 0, "Medium", "", "Brake rotor alternate (qualification pending for caliper)"),
    ("SUP-008", "Massive Dynamic Wire", 2, "JP", "Electrical Components", "Approved", 35, "N", 0, "Medium", "SUP-016", "Wiring and connectors"),
    ("SUP-009", "Cyberdyne Sensors", 1, "US", "Sensors", "Approved", 12, "N", 0, "Low", "", "Sensor primary"),
    ("SUP-010", "Tyrell Optics", 2, "US", "Optics", "Approved", 22, "N", 0, "Medium", "", "Optical sensor backup"),
    ("SUP-011", "Aperture Fluids", 2, "US", "Brake Fluids", "Approved", 8, "N", 0, "Low", "", "Brake fluid supply"),
    ("SUP-012", "Wayne Forgings", 1, "US", "Forgings", "Approved", 19, "N", 0, "Medium", "", "Forged components"),
    ("SUP-013", "Stark Composites", 1, "US", "Composites", "Approved", 25, "N", 0, "Medium", "", "Composite trim"),
    ("SUP-014", "Oscorp Adhesives", 2, "US", "Adhesives", "Approved", 11, "N", 0, "Low", "", "Adhesive supply"),
    ("SUP-015", "Umbrella Coatings", 2, "DE", "Coatings", "Approved", 30, "N", 0, "Medium", "", "Coating services"),
    ("SUP-016", "Nakatomi Electronics", 1, "JP", "Electronics", "Approved", 32, "N", 0, "Medium", "SUP-008", "Electronics alternate"),
    ("SUP-017", "Vandelay Plastics", 2, "US", "Plastics", "Approved", 9, "N", 0, "Low", "", "Plastic components"),
    ("SUP-018", "Wonka Lubricants", 2, "US", "Lubricants", "Approved", 6, "N", 0, "Low", "", "Lubricants"),
    ("SUP-019", "Hanso Hydraulics", 1, "KR", "Hydraulics", "Approved", 27, "N", 0, "Medium", "", "Hydraulic systems"),
    ("SUP-020", "Spacely Springs", 2, "US", "Springs", "Approved", 8, "N", 0, "Low", "", "Springs"),
    ("SUP-021", "Cogswell Cogs", 2, "US", "Gears", "Approved", 9, "N", 0, "Low", "", "Gear assemblies"),
    ("SUP-022", "Tessier-Ashpool Bearings", 1, "JP", "Bearings", "Approved", 30, "N", 0, "Medium", "", "Bearing supply"),
    ("SUP-023", "Yutani Castings", 1, "MX", "Castings", "Approved", 20, "N", 0, "Medium", "SUP-005", "Casting alternate"),
    ("SUP-024", "MomCorp Servos", 1, "US", "Servos", "Approved", 15, "N", 0, "Medium", "", "Servo motors"),
    ("SUP-025", "Buy n Large Boards", 2, "CN", "PCBs", "Approved", 40, "N", 0, "High", "", "PCB assemblies"),
    ("SUP-026", "Encom Firmware", 2, "US", "Firmware Services", "Approved", 14, "N", 0, "Low", "", "Firmware programming"),
    ("SUP-027", "Rekall Memory", 1, "US", "Memory Modules", "Approved", 16, "N", 0, "Medium", "", "Memory modules"),
    ("SUP-028", "Veridian Dynamics Trim", 2, "US", "Interior Trim", "Approved", 7, "N", 0, "Low", "", "Interior trim"),
]

# (Part_ID, Part_Name, Supplier_ID, Plant_ID, Plant_Code, Line_ID, Equipment_ID,
#  Qty_Per_Assy, Effective_Date, Safety_Critical, Alt_Source_Status)
_PARTS: list[tuple[Any, ...]] = [
    ("BRK-CAL-XYZ", "Brake Caliper Assembly", "SUP-001", "plant7", "MMC_P7", "L1", "L1-PRS-001", 1, "2025-01-01", "Y", "NO_DIRECT_ALT"),
    ("STM-PNL-A1", "Stamped Panel A1", "SUP-002", "plant7", "MMC_P7", "L1", "L1-PRS-001", 2, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("ROB-ARM-G3", "Robot Arm Gen3", "SUP-003", "plant7", "MMC_P7", "L2", "L2-ROB-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("FST-M8-100", "M8 Fastener Pack", "SUP-004", "plant7", "MMC_P7", "L1", "L1-PRS-002", 50, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("CST-HSG-04", "Cast Housing 04", "SUP-005", "plant7", "MMC_P7", "L3", "L3-CNV-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("BRK-PAD-STD", "Brake Pad Standard", "SUP-001", "plant7", "MMC_P7", "L1", "L1-PRS-001", 4, "2025-01-01", "Y", "APPROVED_ALT_AVAILABLE"),
    ("BRK-ROT-090", "Brake Rotor 090mm", "SUP-007", "plant7", "MMC_P7", "L1", "L1-PRS-001", 1, "2025-01-01", "Y", "APPROVED_ALT_AVAILABLE"),
    ("BRK-FLD-DOT4", "Brake Fluid DOT4", "SUP-011", "plant7", "MMC_P7", "L1", "L1-PRS-002", 1, "2025-01-01", "Y", "APPROVED_ALT_AVAILABLE"),
    ("STM-PNL-B2", "Stamped Panel B2", "SUP-002", "plant7", "MMC_P7", "L1", "L1-PRS-002", 2, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("STM-PNL-C3", "Stamped Panel C3", "SUP-006", "plant7", "MMC_P7", "L1", "L1-PRS-002", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("FRG-LNK-077", "Forged Link 077", "SUP-012", "plant7", "MMC_P7", "L1", "L1-PRS-002", 2, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("ROB-ARM-G4", "Robot Arm Gen4", "SUP-003", "plant7", "MMC_P7", "L2", "L2-ROB-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("ELC-HRN-12V", "12V Wiring Harness", "SUP-008", "plant7", "MMC_P7", "L2", "L2-ROB-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("ELC-PCB-MAIN", "Main PCB Assembly", "SUP-025", "plant7", "MMC_P7", "L2", "L2-ROB-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("ELC-MEM-08G", "Memory Module 8G", "SUP-027", "plant7", "MMC_P7", "L2", "L2-ROB-001", 2, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("ELC-FW-LOAD", "Firmware Programming", "SUP-026", "plant7", "MMC_P7", "L2", "L2-ROB-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("SNS-PRX-001", "Proximity Sensor 001", "SUP-009", "plant7", "MMC_P7", "L2", "L2-ROB-001", 2, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("SNS-PRX-002", "Proximity Sensor 002", "SUP-009", "plant7", "MMC_P7", "L2", "L2-ROB-001", 2, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("OPT-LNS-002", "Optical Lens 002", "SUP-010", "plant7", "MMC_P7", "L3", "L3-CNV-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("OPT-FLT-002", "Optical Filter 002", "SUP-010", "plant7", "MMC_P7", "L3", "L3-CNV-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("CST-HSG-05", "Cast Housing 05", "SUP-005", "plant7", "MMC_P7", "L3", "L3-CNV-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("CST-HSG-06", "Cast Housing 06", "SUP-023", "plant7", "MMC_P7", "L3", "L3-CNV-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("BRG-RAD-090", "Radial Bearing 090", "SUP-022", "plant7", "MMC_P7", "L3", "L3-CNV-001", 2, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("LUB-OIL-MULTI", "Multi-purpose Oil", "SUP-018", "plant7", "MMC_P7", "L3", "L3-CNV-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("ADH-CYAN-50ML", "Cyanoacrylate 50ml", "SUP-014", "plant7", "MMC_P7", "L3", "L3-CNV-001", 4, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("SPR-COIL-022", "Coil Spring 022", "SUP-020", "plant7", "MMC_P7", "L1", "L1-PRS-001", 4, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("SPR-LEAF-118", "Leaf Spring 118", "SUP-020", "plant7", "MMC_P7", "L1", "L1-PRS-001", 2, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("GEAR-PIN-018", "Pinion Gear 018", "SUP-021", "plant7", "MMC_P7", "L2", "L2-ROB-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("GEAR-SPR-024", "Spur Gear 024", "SUP-021", "plant7", "MMC_P7", "L2", "L2-ROB-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("CMP-TRIM-A", "Composite Trim A", "SUP-013", "plant7", "MMC_P7", "L3", "L3-CNV-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("CMP-TRIM-B", "Composite Trim B", "SUP-013", "plant7", "MMC_P7", "L3", "L3-CNV-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("CTG-PAINT-WHT", "White Paint Coating", "SUP-015", "plant7", "MMC_P7", "L3", "L3-CNV-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("CTG-PAINT-BLK", "Black Paint Coating", "SUP-015", "plant7", "MMC_P7", "L3", "L3-CNV-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("SRV-MOTOR-220", "Servo Motor 220", "SUP-024", "plant7", "MMC_P7", "L2", "L2-ROB-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("SRV-MOTOR-330", "Servo Motor 330", "SUP-024", "plant7", "MMC_P7", "L2", "L2-ROB-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("HYD-PUMP-A", "Hydraulic Pump A", "SUP-019", "plant7", "MMC_P7", "L1", "L1-PRS-001", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("HYD-PUMP-B", "Hydraulic Pump B", "SUP-019", "plant7", "MMC_P7", "L1", "L1-PRS-002", 1, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("PLA-CLIP-A", "Plastic Clip A", "SUP-017", "plant7", "MMC_P7", "L3", "L3-CNV-001", 10, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("PLA-CLIP-B", "Plastic Clip B", "SUP-017", "plant7", "MMC_P7", "L3", "L3-CNV-001", 10, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("TRIM-INT-001", "Interior Trim 001", "SUP-028", "plant7", "MMC_P7", "L3", "L3-CNV-001", 2, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
    ("TRIM-INT-002", "Interior Trim 002", "SUP-028", "plant7", "MMC_P7", "L3", "L3-CNV-001", 2, "2025-01-01", "N", "APPROVED_ALT_AVAILABLE"),
]

_PROGRAMS = [
    ("EV-BRK-26", "EV Brake Platform 26", "Northstar EV"),
    ("MMC-BODY-25", "Body Refresh 25", "Northstar EV"),
    ("MMC-AUTO-24", "Auto Cell Sustaining 24", "MidOEM"),
    ("MMC-GEN", "General Service Parts", "Internal"),
    ("MMC-CAST-25", "Casting Program 25", "Heavy Inc"),
]


def _program_for(part_id: str) -> str:
    return PROGRAM_CODES.get(part_id[:3], "MMC-GEN")


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
        ["Supplier_ID", "Supplier_Name", "Tier", "Country", "Primary_Commodity",
         "Qualification_Status", "Lead_Time_Days", "Disruption_Flag",
         "Disruption_Days", "Risk_Score", "Preferred_Alt_Supplier_ID", "Notes"],
        [list(s) for s in _SUPPLIERS],
    )
    _write_csv(
        out / "bom_where_used.csv",
        ["Part_ID", "Part_Name", "Supplier_ID", "Plant_ID", "Plant_Code",
         "Line_ID", "Equipment_ID", "Qty_Per_Assy", "Effective_Date",
         "Safety_Critical", "Alt_Source_Status"],
        [list(p) for p in _PARTS],
    )
    inv_rows = []
    for p in _PARTS:
        part_id = p[0]
        qty = p[7]
        on_hand = (hash(part_id) % 400) + 50
        allocated = max(0, on_hand - (hash(part_id + "alloc") % 100))
        dos = max(1, (hash(part_id + "dos") % 60) + 4)
        reorder = qty * 10 + 20
        inv_rows.append([part_id, "plant7", "MMC_P7-CRIB", on_hand, allocated, dos, reorder])
    # Special-case BRK-CAL-XYZ (matches plan sample for storytelling)
    for r in inv_rows:
        if r[0] == "BRK-CAL-XYZ":
            r[3], r[4], r[5], r[6] = 32, 28, 4, 50
    _write_csv(
        out / "erp_inventory.csv",
        ["Part_ID", "Plant_ID", "Stocking_Location", "On_Hand_Qty",
         "Allocated_Qty", "Days_Of_Supply", "Reorder_Point"],
        inv_rows,
    )
    carriers = ["NorthStar Logistics", "Lake Freight", "EuroLink Air",
                "Midwest LTL", "Borderline Freight", "Pacific Cargo", "Atlas Rail"]
    statuses = ["On Time", "Watch", "Delayed", "On Time", "On Time"]
    freight_rows = []
    for i, p in enumerate(_PARTS):
        part_id, _, supplier_id, *_ = p
        sup = next(s for s in _SUPPLIERS if s[0] == supplier_id)
        country = sup[3]
        carrier = carriers[i % len(carriers)]
        status = "Delayed" if part_id == "BRK-CAL-XYZ" else statuses[i % len(statuses)]
        delay = 21 if part_id == "BRK-CAL-XYZ" else (2 if status == "Watch" else 0)
        eta_month = (i % 3) + 2
        eta_day = (i % 27) + 1
        origin = {"US": "Indianapolis IN", "DE": "Hamburg DE", "MX": "Monterrey MX",
                  "JP": "Yokohama JP", "KR": "Busan KR", "CN": "Shenzhen CN"}.get(country, "Origin")
        freight_rows.append([
            f"TMS-{i+1:04d}", supplier_id, part_id, carrier,
            origin, "MMC_P7 Receiving",
            f"2026-{eta_month:02d}-{eta_day:02d}", status, delay,
        ])
    _write_csv(
        out / "tms_freight.csv",
        ["Shipment_ID", "Supplier_ID", "Part_ID", "Carrier", "Origin",
         "Destination", "ETA_Date", "Status", "Delay_Days"],
        freight_rows,
    )


# --- procurement ----------------------------------------------------------

def _gen_procurement(out: Path, seed: dict) -> None:
    contracts = []
    contract_types = ["LTA", "LTA", "LTA", "Blanket", "Spot"]
    incoterms = ["FCA", "DAP", "FCA", "DAP", "FCA"]
    for i, p in enumerate(_PARTS):
        part_id, _, supplier_id, *_ = p
        unit_price = round(0.10 + (hash(part_id + "u") % 19000) * 0.01, 2)
        expedite = "Y" if i % 2 == 0 else "N"
        exp_cost = round(unit_price * 0.12, 2) if expedite == "Y" else 0.00
        contracts.append([
            f"CON-{i+1:04d}", supplier_id, part_id,
            contract_types[i % 5], incoterms[i % 5],
            expedite, exp_cost, "USD", "Net 45",
            "2025-01-01", "2026-12-31",
        ])
    # Anchor BRK-CAL-XYZ to plan-sample values for storytelling parity
    for c in contracts:
        if c[2] == "BRK-CAL-XYZ":
            c[3:11] = ["LTA", "FCA", "Y", 18.50, "USD", "Net 45", "2025-01-01", "2026-12-31"]
    _write_csv(
        out / "contracts.csv",
        ["Contract_ID", "Supplier_ID", "Part_ID", "Contract_Type", "Incoterms",
         "Expedite_Allowed", "Expedite_Cost_Per_Unit", "Currency",
         "Payment_Terms", "Effective_Date", "Expiration_Date"],
        contracts,
    )
    po = []
    statuses = ["Open", "Watch", "Open", "Open", "Open"]
    for i, p in enumerate(_PARTS):
        part_id, _, supplier_id, plant_id, *_ = p
        unit = round(0.10 + (hash(part_id + "p") % 19000) * 0.01, 2)
        qty = ((hash(part_id) % 90) + 10) * 10
        ext = round(qty * unit, 2)
        status = "At Risk" if part_id == "BRK-CAL-XYZ" else statuses[i % 5]
        po.append([
            f"PO-{i+1:05d}", supplier_id, part_id, plant_id,
            "2026-01-05", "2026-02-04", qty, unit, ext, status,
        ])
    for r in po:
        if r[2] == "BRK-CAL-XYZ":
            r[6], r[7], r[8] = 480, 142.00, 68160.00
    _write_csv(
        out / "po_spend.csv",
        ["PO_ID", "Supplier_ID", "Part_ID", "Plant_ID", "Order_Date",
         "Need_Date", "Open_Qty", "Unit_Price", "Extended_Value", "Status"],
        po,
    )
    sc = []
    for p in _PARTS:
        part_id = p[0]
        mat = round(0.05 + (hash(part_id + "m") % 13000) * 0.01, 2)
        labor = round(mat * 0.10, 2)
        oh = round(mat * 0.20, 2)
        freight = round(mat * 0.05, 2)
        should = round(mat + labor + oh + freight, 2)
        current = round(should * 1.20, 2)
        variance = round((current - should) / should * 100, 2) if should else 0.0
        sc.append([part_id, mat, labor, oh, freight, should, current, variance])
    for r in sc:
        if r[0] == "BRK-CAL-XYZ":
            r[1:] = [82.00, 12.00, 18.00, 6.00, 118.00, 142.00, 20.34]
    _write_csv(
        out / "should_cost_model.csv",
        ["Part_ID", "Material_Cost", "Labor_Cost", "Overhead_Cost",
         "Freight_Cost", "Should_Cost", "Current_Unit_Price", "Variance_Percent"],
        sc,
    )


# --- engineering-plm ------------------------------------------------------

def _gen_engineering_plm(out: Path, seed: dict) -> None:
    materials = {"BRK": "Ductile Iron", "STM": "HSLA Steel", "ROB": "Aluminum",
                 "FST": "Steel", "CST": "Aluminum", "ELC": "Composite",
                 "SNS": "Polymer", "OPT": "Glass", "FRG": "Steel",
                 "BRG": "Steel", "LUB": "Synthetic", "ADH": "Polymer",
                 "SPR": "Spring Steel", "GEAR": "Steel", "CMP": "Composite",
                 "CTG": "Coating", "SRV": "Steel", "HYD": "Steel",
                 "PLA": "Polymer", "TRIM": "Polymer"}
    engineers = ["Dana Patel", "Riley Chen", "Jordan Lee", "Sam Rivera",
                 "Avery Kim", "Morgan Brooks", "Casey Park"]
    pm = []
    for i, p in enumerate(_PARTS):
        part_id, name, _, _, _, _, _, _, _, safety, _ = p
        rev = "C" if part_id == "BRK-CAL-XYZ" else (["A", "B"][i % 2])
        material = materials.get(part_id.split("-")[0], "Steel")
        pm.append([part_id, name, rev, "Released", material, safety,
                   _program_for(part_id), engineers[i % len(engineers)]])
    _write_csv(
        out / "plm_part_master.csv",
        ["Part_ID", "Part_Name", "Revision", "Lifecycle_State", "Material",
         "Safety_Critical", "Program_Code", "Owning_Engineer"],
        pm,
    )
    eco = []
    reasons = ["Material change for cost reduction", "Tolerance tightening",
               "Supplier casting process update", "Cable routing update",
               "Wall thickness optimization", "Process refinement"]
    statuses = ["Released", "Released", "In Review", "Closed", "Released"]
    for i, p in enumerate(_PARTS):
        part_id, _, _, _, _, _, _, _, _, safety, _ = p
        from_rev = "A"
        to_rev = "C" if part_id == "BRK-CAL-XYZ" else "B"
        status = "Released" if part_id == "BRK-CAL-XYZ" else statuses[i % 5]
        approved = "" if status == "In Review" else "2026-01-10"
        eco.append([
            f"ECO-2026-{i+14:03d}", part_id, from_rev, to_rev, status,
            reasons[i % len(reasons)], "2025-12-15", approved, safety,
        ])
    _write_csv(
        out / "eco_log.csv",
        ["ECO_ID", "Part_ID", "Revision_From", "Revision_To", "Status",
         "Reason", "Opened_Date", "Approved_Date", "Safety_Review_Required"],
        eco,
    )
    eff = []
    for i, p in enumerate(_PARTS):
        part_id, _, _, plant_id, _, line_id, *_ = p
        rev = "C" if part_id == "BRK-CAL-XYZ" else "A"
        eff.append([
            f"EFF-{i+1:04d}", part_id, rev, plant_id, line_id,
            "2026-01-15", "", _program_for(part_id),
        ])
    _write_csv(
        out / "effectivity.csv",
        ["Effectivity_ID", "Part_ID", "Revision", "Plant_ID", "Line_ID",
         "Effective_From", "Effective_To", "Program_Code"],
        eff,
    )


# --- enterprise-quality ---------------------------------------------------

def _gen_enterprise_quality(out: Path, seed: dict) -> None:
    bc_part = seed["brake_caliper"]["part_id"]
    modes = ["Brake drag", "Caliper seal leak", "Brake noise",
             "Caliper binding", "Brake drag"]
    customers = ["Northstar EV", "Northstar EV", "Great Lakes Fleet",
                 "Northstar EV", "Northstar EV"]
    claims = []
    # 10 anchored BRK-CAL-XYZ rows
    for i in range(10):
        date = f"2026-01-{(i*3)+5:02d}"
        claims.append([
            f"WCL-2026-{i+1:04d}", bc_part, "plant7", "L1",
            customers[i % len(customers)], modes[i % len(modes)],
            "High" if i % 3 != 2 else "Medium", date, "Open",
        ])
    # Plus 25 rows across other parts
    other_modes = ["Cosmetic", "Sensor fault", "Wear", "Fit issue", "Vibration"]
    for i, p in enumerate(_PARTS):
        if p[0] == bc_part:
            continue
        part_id = p[0]
        for j in range(1):
            idx = 11 + i
            claims.append([
                f"WCL-2026-{idx:04d}", part_id, "plant7", p[5],
                customers[idx % len(customers)],
                other_modes[idx % len(other_modes)],
                ["Low", "Medium", "Low"][idx % 3],
                f"2026-02-{(idx % 27) + 1:02d}", "Open",
            ])
    _write_csv(
        out / "warranty_claims.csv",
        ["Claim_ID", "Part_ID", "Plant_ID", "Line_ID", "Customer",
         "Failure_Mode", "Severity", "Claim_Date", "Status"],
        claims,
    )
    feed = []
    symptoms = ["Brake drag after cold start", "Fluid at caliper seal",
                "Audible brake noise", "Right front brake drag",
                "Caliper binding during inspection"]
    sources = ["OEM Portal", "Dealer Report", "OEM Portal",
               "Fleet Telematics", "Dealer Report"]
    for i in range(10):
        feed.append([
            f"FFF-{i+1:04d}", bc_part, sources[i % len(sources)],
            f"2026-01-{(i*3)+5:02d}", symptoms[i % len(symptoms)],
            "Y" if i % 3 != 2 else "N", f"WCL-2026-{i+1:04d}",
        ])
    for i, p in enumerate(_PARTS):
        if p[0] == bc_part:
            continue
        idx = 11 + i
        feed.append([
            f"FFF-{idx:04d}", p[0], sources[idx % len(sources)],
            f"2026-02-{(idx % 27) + 1:02d}",
            f"{p[1]} observation", "N", f"WCL-2026-{idx:04d}",
        ])
    _write_csv(
        out / "field_failure_feed.csv",
        ["Feed_ID", "Part_ID", "Source", "Signal_Date", "Symptom_Text",
         "Potential_Safety", "Linked_Claim_ID"],
        feed,
    )
    _write_csv(
        out / "recall_ruleset.csv",
        ["Rule_ID", "Part_Family", "Metric", "Threshold_Count", "Window_Days",
         "Action", "Applies_To_Safety_Critical"],
        [
            ["REC-001", "Brake", "High severity claims", 5, 60, "Open safety review", "Y"],
            ["REC-002", "Brake", "Potential safety field failures", 3, 60, "Escalate to recall council", "Y"],
            ["REC-003", "General", "Repeat cosmetic claims", 20, 90, "Quality trend review", "N"],
            ["REC-004", "Robot", "Unexpected motion reports", 2, 30, "EHS engineering review", "Y"],
            ["REC-005", "Conveyor", "Jam-related injuries", 3, 90, "Containment review", "Y"],
        ],
    )


# --- demand-program -------------------------------------------------------

def _gen_demand_program(out: Path, seed: dict) -> None:
    bc_part = seed["brake_caliper"]["part_id"]
    signal_types = ["Pull-ahead", "Firm", "Firm", "Forecast", "Firm"]
    orders = []
    # Anchored BRK-CAL-XYZ rows
    bc_orders = [
        ("CRM-ORD-0001", "Northstar EV", "EV-BRK-26", bc_part, "2026-W06", 250, "Pull-ahead", "High"),
        ("CRM-ORD-0002", "Northstar EV", "EV-BRK-26", bc_part, "2026-W07", 275, "Firm", "High"),
        ("CRM-ORD-0003", "Great Lakes Fleet", "EV-BRK-26", bc_part, "2026-W08", 180, "Firm", "High"),
        ("CRM-ORD-0004", "Northstar EV", "EV-BRK-26", bc_part, "2026-W09", 300, "Forecast", "Normal"),
    ]
    orders.extend(list(r) for r in bc_orders)
    for i, p in enumerate(_PARTS):
        if p[0] == bc_part:
            continue
        idx = 5 + i
        program = _program_for(p[0])
        customer = next(pr[2] for pr in _PROGRAMS if pr[0] == program)
        qty = ((hash(p[0]) % 90) + 10) * 10
        orders.append([
            f"CRM-ORD-{idx:04d}", customer, program, p[0],
            f"2026-W{(idx % 50) + 1:02d}", qty,
            signal_types[idx % len(signal_types)], "Normal",
        ])
    _write_csv(
        out / "order_crm_feed.csv",
        ["Order_ID", "Customer", "Program_Code", "Part_ID", "Requested_Week",
         "Order_Qty", "Signal_Type", "Priority"],
        orders,
    )
    plan_rows = [
        ["EV-BRK-26", "Brake system launch readiness", "Program Mgmt", "2026-03-01", "At Risk", "Supplier disruption affects L1 brake caliper build"],
        ["EV-BRK-26", "Customer PPAP confirmation", "Quality", "2026-02-20", "At Risk", "Warranty claims under review"],
        ["MMC-BODY-25", "Panel refresh launch", "Engineering", "2026-04-15", "Green", "No material risk"],
        ["MMC-AUTO-24", "Robot cell sustaining", "Ops", "2026-03-30", "Green", "No material risk"],
        ["MMC-GEN", "General service parts", "Supply Chain", "2026-02-28", "Green", "No material risk"],
        ["MMC-CAST-25", "Cast housing program review", "Engineering", "2026-05-15", "Green", "No material risk"],
    ]
    _write_csv(
        out / "program_plan.csv",
        ["Program_Code", "Milestone", "Owner", "Due_Date", "Status", "Risk"],
        plan_rows,
    )
    alloc = []
    # Anchored BRK-CAL-XYZ allocations (constrained)
    for i, qty in enumerate([250, 275, 180], start=1):
        alloc.append([f"ALLOC-{i:04d}", "EV-BRK-26", bc_part, "plant7", "L1", qty, "Constrained"])
    # One row per remaining part
    next_idx = 4
    for p in _PARTS:
        if p[0] == bc_part:
            continue
        qty = ((hash(p[0]) % 90) + 10) * 10
        alloc.append([
            f"ALLOC-{next_idx:04d}", _program_for(p[0]), p[0],
            p[3], p[5], qty, "Available",
        ])
        next_idx += 1
    _write_csv(
        out / "allocation_model.csv",
        ["Allocation_ID", "Program_Code", "Part_ID", "Plant_ID", "Line_ID",
         "Allocated_Qty", "Capacity_Status"],
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", action="append", default=None,
                        help="Node name (repeatable). Defaults to all.")
    args = parser.parse_args(argv)
    seed = yaml.safe_load((ROOT / "enterprise" / "scenario_seed.yaml").read_text(encoding="utf-8"))
    nodes = args.node or list(NODE_SPECS)
    for node in nodes:
        out_dir = ROOT / "enterprise" / node / "data"
        generate_node(node, out_dir, seed)
        print(f"generated {node} -> {out_dir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
