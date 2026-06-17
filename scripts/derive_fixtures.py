"""Derive tool fixtures (JSON keyed by lookup field) from enterprise CSVs.

Single source of truth: CSVs in `enterprise/<node>/data/`.
Fixtures in `enterprise/<node>/fixtures/` are regenerable byte-identically.

For 1-row-per-key tables, the JSON is `{key: row}`.
For 1-key-to-many tables (PO, ECO, warranty, etc.), the JSON is
`{key: [row, ...]}` so tools can return lists.

CLI: `python -m scripts.derive_fixtures [--node NAME ...]`
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (csv_path, fixture_path, key_column, multi)
ONE = False
MULTI = True

MAPPINGS: dict[str, list[tuple[str, str, str, bool]]] = {
    "supply-chain": [
        ("enterprise/supply-chain/data/supplier_master.csv",
         "enterprise/supply-chain/fixtures/supplier_master.json",
         "Supplier_ID", ONE),
        ("enterprise/supply-chain/data/bom_where_used.csv",
         "enterprise/supply-chain/fixtures/bom_where_used.json",
         "Part_ID", ONE),
        ("enterprise/supply-chain/data/erp_inventory.csv",
         "enterprise/supply-chain/fixtures/erp_inventory.json",
         "Part_ID", ONE),
        ("enterprise/supply-chain/data/tms_freight.csv",
         "enterprise/supply-chain/fixtures/tms_freight.json",
         "Shipment_ID", ONE),
    ],
    "procurement": [
        ("enterprise/procurement/data/contracts.csv",
         "enterprise/procurement/fixtures/contracts.json",
         "Part_ID", MULTI),
        ("enterprise/procurement/data/po_spend.csv",
         "enterprise/procurement/fixtures/po.json",
         "Part_ID", MULTI),
        ("enterprise/procurement/data/should_cost_model.csv",
         "enterprise/procurement/fixtures/should_cost_model.json",
         "Part_ID", ONE),
    ],
    "engineering-plm": [
        ("enterprise/engineering-plm/data/plm_part_master.csv",
         "enterprise/engineering-plm/fixtures/plm_part_master.json",
         "Part_ID", ONE),
        ("enterprise/engineering-plm/data/eco_log.csv",
         "enterprise/engineering-plm/fixtures/eco_log.json",
         "Part_ID", MULTI),
        ("enterprise/engineering-plm/data/effectivity.csv",
         "enterprise/engineering-plm/fixtures/effectivity.json",
         "Part_ID", MULTI),
    ],
    "enterprise-quality": [
        ("enterprise/enterprise-quality/data/warranty_claims.csv",
         "enterprise/enterprise-quality/fixtures/warranty_claims.json",
         "Part_ID", MULTI),
        ("enterprise/enterprise-quality/data/field_failure_feed.csv",
         "enterprise/enterprise-quality/fixtures/field_failure_feed.json",
         "Part_ID", MULTI),
        ("enterprise/enterprise-quality/data/recall_ruleset.csv",
         "enterprise/enterprise-quality/fixtures/recall_ruleset.json",
         "Rule_ID", ONE),
    ],
    "demand-program": [
        ("enterprise/demand-program/data/order_crm_feed.csv",
         "enterprise/demand-program/fixtures/order_crm_feed.json",
         "Part_ID", MULTI),
        ("enterprise/demand-program/data/program_plan.csv",
         "enterprise/demand-program/fixtures/program_plan.json",
         "Program_Code", MULTI),
        ("enterprise/demand-program/data/allocation_model.csv",
         "enterprise/demand-program/fixtures/allocation_model.json",
         "Part_ID", MULTI),
    ],
}

PLANT_MAPPINGS: dict[str, list[tuple[str, str, str, bool]]] = {
    "plant7": [
        ("plants/plant7/data/capa.csv",
         "plants/plant7/fixtures/capa.json", "CAPA_ID", ONE),
        ("plants/plant7/data/cmms.csv",
         "plants/plant7/fixtures/cmms.json", "PM_ID", ONE),
        ("plants/plant7/data/qms.csv",
         "plants/plant7/fixtures/qms.json", "NCR_ID", ONE),
        ("plants/plant7/data/scada.csv",
         "plants/plant7/fixtures/scada.json", "Asset_ID", ONE),
        ("plants/plant7/data/mes.csv",
         "plants/plant7/fixtures/mes.json", "Schedule_ID", ONE),
        ("plants/plant7/data/lms.csv",
         "plants/plant7/fixtures/lms.json", "Training_ID", ONE),
    ],
}


def derive(csv_path: Path, fixture_path: Path, key: str, multi: bool) -> None:
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    if multi:
        out: dict[str, list[dict]] = {}
        for row in rows:
            out.setdefault(row[key], []).append(row)
    else:
        out = {row[key]: row for row in rows}
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(
        json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", action="append", default=None,
                        help="Enterprise node name (repeatable). Defaults to all.")
    parser.add_argument("--plant", action="append", default=None,
                        help="Plant name (repeatable). e.g. plant7")
    args = parser.parse_args(argv)
    do_enterprise = args.node is not None or args.plant is None
    if args.node == ["all"]:
        nodes = list(MAPPINGS)
    else:
        nodes = args.node if args.node else (list(MAPPINGS) if do_enterprise else [])
    plants = args.plant or ([] if args.node else list(PLANT_MAPPINGS))
    total = 0
    for node in nodes:
        for csv_rel, fix_rel, key, multi in MAPPINGS[node]:
            derive(ROOT / csv_rel, ROOT / fix_rel, key, multi)
            total += 1
        print(f"derived {node} -> {len(MAPPINGS[node])} fixtures")
    for plant in plants:
        for csv_rel, fix_rel, key, multi in PLANT_MAPPINGS[plant]:
            derive(ROOT / csv_rel, ROOT / fix_rel, key, multi)
            total += 1
        print(f"derived {plant} -> {len(PLANT_MAPPINGS[plant])} fixtures")
    print(f"Derived {total} fixtures total.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
