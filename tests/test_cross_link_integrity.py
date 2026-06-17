"""Cross-link integrity (Gate B Task 11).

Ensures the brake-caliper story and LOTO cluster cross-link cleanly across
enterprise CSVs and Plant 7 logs.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_csv(path: Path) -> list[dict]:
    return list(csv.DictReader(path.open(encoding="utf-8-sig")))


def test_brake_caliper_resolves_enterprise_to_plant7_records():
    suppliers = load_csv(ROOT / "enterprise" / "supply-chain" / "data" / "supplier_master.csv")
    bom = load_csv(ROOT / "enterprise" / "supply-chain" / "data" / "bom_where_used.csv")
    pm = load_csv(ROOT / "plants" / "plant7" / "kb" / "08_Logs_Data" / "MMC_P7_PM_Schedule.csv")
    incidents = load_csv(ROOT / "plants" / "plant7" / "kb" / "08_Logs_Data" / "MMC_P7_Incident_Log.csv")

    acme = next(r for r in suppliers if r["Supplier_ID"] == "SUP-001")
    brake = next(r for r in bom if r["Part_ID"] == "BRK-CAL-XYZ")
    assert acme["Supplier_Name"] == "Acme Brakes"
    assert brake["Plant_ID"] == "plant7" and brake["Line_ID"] == "L1"
    assert any(
        r.get("Asset_ID") == brake["Equipment_ID"] or r.get("Location") in {"L1", "Line 1"}
        for r in pm
    )
    assert any(
        r.get("Location") in {"L1", "Line 1"} or r.get("Area") in {"L1", "Line 1"}
        for r in incidents
    )


def test_loto_cluster_has_three_l1_near_misses():
    incidents = load_csv(ROOT / "plants" / "plant7" / "kb" / "08_Logs_Data" / "MMC_P7_Incident_Log.csv")
    hits = [
        r for r in incidents
        if r.get("Location") in {"L1", "Line 1"}
        and "LOTO" in (r.get("Description", "") + r.get("Root_Cause", "")).upper()
    ]
    assert len(hits) >= 3, f"expected ≥3 L1 LOTO near-misses, got {len(hits)}: {[h['Incident_ID'] for h in hits]}"
