"""Tests for scripts/generate_plant_content.py (Gate D Task 7).

Defines the contract for the plant content generator before the script
exists (TDD red phase). The generator has two phases:

1. *Mechanical* substitution of plant-local CSV identifiers (P7-Lx-* to
   P4-Lx-*, PM-P7- to PM-P4-, etc.) plus deterministic jitter on dates
   and quantities seeded from sha256(plant_id:filename:row_index).
2. *Narrative* LLM regeneration of KB markdown — out of scope for Task 7
   (covered in Task 9).

These tests use ``--mechanical-only`` to exercise phase 1 in isolation
without an LLM dependency.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_plant_content.py"

SAMPLE_CSV_HEADER = "PM_ID,Asset_ID,Scheduled_Date,Duration_Hours,Notes\n"
SAMPLE_CSV_ROW = "PM-P7-001,P7-L1-CMM-04,2026-01-10,2.0,BRK-CAL-XYZ stays shared\n"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def _make_plant4(plants_root: Path) -> Path:
    """Materialize a minimal plant4 directory (post-clone shape) under plants_root."""
    plant_dir = plants_root / "plant4"
    csv_dir = plant_dir / "kb" / "08_Logs_Data"
    csv_dir.mkdir(parents=True, exist_ok=True)
    (csv_dir / "MMC_P4_PM_Schedule.csv").write_text(
        SAMPLE_CSV_HEADER + SAMPLE_CSV_ROW, encoding="utf-8"
    )
    profile = {
        "plant_id": "plant4",
        "plant_code": "P4",
        "display_name": "MMC Plant 4 (Monterrey)",
        "lines": [
            {"id": "L1", "name": "Brake-Caliper Assembly", "equipment_prefix": "L1-CMM-"},
        ],
        "agents": [],
        "kb": {"kb_id_env": "FOUNDRY_IQ_KB_PLANT4_ID"},
    }
    (plant_dir / "profile.yaml").write_text(
        yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
    )
    return plant_dir


@pytest.fixture
def plant4_root(tmp_path: Path) -> Path:
    """Plants root containing a minimal plant4 ready for mechanical generation."""
    plants_root = tmp_path / "plants"
    plants_root.mkdir()
    _make_plant4(plants_root)
    return plants_root


def test_mechanical_substitutes_plant_tokens(plant4_root: Path) -> None:
    """Plant 7 identifiers are rewritten to Plant 4; shared scenario IDs persist."""
    csv_path = plant4_root / "plant4" / "kb" / "08_Logs_Data" / "MMC_P4_PM_Schedule.csv"
    result = _run([
        "--plant", "plant4",
        "--plants-root", str(plant4_root),
        "--mechanical-only",
    ])
    assert result.returncode == 0, (
        f"generator failed:\nstderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    )

    rendered = csv_path.read_text(encoding="utf-8")
    # Header is part of the schema contract; never mutated.
    assert rendered.startswith(SAMPLE_CSV_HEADER), "CSV header must be preserved"

    # Plant 4 stamps appear...
    assert "P4-L1-CMM-04" in rendered, "expected equipment ID rewritten to P4-*"
    assert "PM-P4-" in rendered, "expected work-order prefix rewritten to PM-P4-"
    # ...Plant 7 stamps gone...
    assert "P7-L1-CMM-04" not in rendered, "stale P7-L1-CMM-04 must be rewritten"
    assert "PM-P7-" not in rendered, "stale PM-P7- prefix must be rewritten"
    # ...cross-plant scenario IDs untouched.
    assert "BRK-CAL-XYZ" in rendered, (
        "BRK-CAL-XYZ is a cross-plant shared part; must not be rewritten"
    )


def test_mechanical_phase_is_deterministic(plant4_root: Path) -> None:
    """Two consecutive runs produce byte-identical CSV output (no nondeterminism)."""
    csv_path = plant4_root / "plant4" / "kb" / "08_Logs_Data" / "MMC_P4_PM_Schedule.csv"

    args = [
        "--plant", "plant4",
        "--plants-root", str(plant4_root),
        "--mechanical-only",
    ]
    r1 = _run(args)
    assert r1.returncode == 0, f"first run failed: {r1.stderr}"
    first_bytes = csv_path.read_bytes()

    # Reset to pre-run state so the second pass starts from the same input.
    csv_path.write_text(SAMPLE_CSV_HEADER + SAMPLE_CSV_ROW, encoding="utf-8")
    r2 = _run(args)
    assert r2.returncode == 0, f"second run failed: {r2.stderr}"
    second_bytes = csv_path.read_bytes()

    assert first_bytes == second_bytes, (
        "mechanical phase must be byte-deterministic; "
        f"first hash {hashlib.sha256(first_bytes).hexdigest()[:12]}, "
        f"second {hashlib.sha256(second_bytes).hexdigest()[:12]}"
    )


def test_help_lists_mechanical_only_flag() -> None:
    """--help must document --plant, --plants-root, --mechanical-only."""
    result = _run(["--help"])
    assert result.returncode == 0, f"help failed:\n{result.stderr}"
    for flag in ("--plant", "--plants-root", "--mechanical-only"):
        assert flag in result.stdout, f"missing {flag} in --help output"
