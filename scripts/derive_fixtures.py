"""Derive tool fixtures (JSON keyed by lookup field) from enterprise CSVs.

Single source of truth: CSVs in enterprise/<node>/data/.
Fixtures in enterprise/<node>/fixtures/ are regenerable byte-identically.
"""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (csv_path, fixture_path, key_column)
MAPPINGS = [
    (
        "enterprise/supply-chain/data/supplier_master.csv",
        "enterprise/supply-chain/fixtures/supplier_master.json",
        "Supplier_ID",
    ),
    (
        "enterprise/supply-chain/data/bom_where_used.csv",
        "enterprise/supply-chain/fixtures/bom_where_used.json",
        "Part_ID",
    ),
]

def derive(csv_path: Path, fixture_path: Path, key: str) -> None:
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    out: dict[str, dict] = {}
    for row in rows:
        out[row[key]] = row
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(
        json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )

def main() -> None:
    for csv_rel, fix_rel, key in MAPPINGS:
        derive(ROOT / csv_rel, ROOT / fix_rel, key)
    print(f"Derived {len(MAPPINGS)} fixtures.")

if __name__ == "__main__":
    main()
