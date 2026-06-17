"""Tests for scripts/generate_enterprise_data.py (Gate B Task 4)."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_enterprise_data import (  # noqa: E402
    NODE_SPECS,
    generate_node,
)


def _rows(path: Path) -> list[dict]:
    return list(csv.DictReader(path.open(encoding="utf-8")))


def _seed():
    return yaml.safe_load((ROOT / "enterprise" / "scenario_seed.yaml").read_text(encoding="utf-8"))


def test_specs_cover_all_nodes():
    assert set(NODE_SPECS) == {
        "supply-chain",
        "procurement",
        "engineering-plm",
        "enterprise-quality",
        "demand-program",
    }


def test_supply_chain_contains_brake_cross_link(tmp_path: Path):
    generate_node("supply-chain", tmp_path, _seed())
    suppliers = _rows(tmp_path / "supplier_master.csv")
    assert len(suppliers) >= 25
    assert any(s["Supplier_ID"] == "SUP-001" and s["Name"] == "Acme Brakes" for s in suppliers)

    bom = _rows(tmp_path / "bom_where_used.csv")
    assert any(
        r["Part_ID"] == "BRK-CAL-XYZ"
        and r["Plant_ID"] == "plant7"
        and r["Line_ID"] == "L1"
        and r["Supplier_ID"] == "SUP-001"
        for r in bom
    )


def test_all_nodes_produce_all_files(tmp_path: Path):
    seed = _seed()
    for node, files in NODE_SPECS.items():
        target = tmp_path / node
        generate_node(node, target, seed)
        for f in files:
            p = target / f
            assert p.exists(), f"{node}/{f} not generated"
            assert _rows(p), f"{node}/{f} has no rows"


def test_generation_is_deterministic(tmp_path: Path):
    a, b = tmp_path / "a", tmp_path / "b"
    seed = _seed()
    generate_node("procurement", a, seed)
    generate_node("procurement", b, seed)
    for f in NODE_SPECS["procurement"]:
        assert (a / f).read_bytes() == (b / f).read_bytes()
