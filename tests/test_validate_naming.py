"""Tests for scripts/validate_naming.py (Gate B Task 3)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validate_naming import (  # noqa: E402
    validate_equipment_id,
    validate_part_id,
    validate_text,
)


def test_validate_text_accepts_plant7_terms():
    assert validate_text("MMC_P7 L1 L1-PRS-001 OSHA 29 CFR 1910 ISO 45001") == []


def test_validate_text_rejects_wrong_plant_and_line():
    errs = validate_text("MMC_P8 L4 PRESS-1")
    assert "MMC_P8" in errs
    assert "L4" in errs


def test_validate_text_accepts_all_valid_lines():
    assert validate_text("MMC_P7 L1 L2 L3") == []


def test_part_id_accepts_brake_caliper():
    assert validate_part_id("BRK-CAL-XYZ") == []


def test_part_id_rejects_garbage():
    assert validate_part_id("not-a-part") == ["not-a-part"]


def test_equipment_id_accepts_l1_press():
    assert validate_equipment_id("L1-PRS-001") == []


def test_equipment_id_rejects_unknown_kind():
    assert validate_equipment_id("L1-XYZ-001") == ["L1-XYZ-001"]
