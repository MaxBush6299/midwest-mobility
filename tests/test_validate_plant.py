"""Contract tests for scripts/validate_plant.py (Gate D Tasks 11, 12, 13).

The validator inspects a cloned plant directory and emits a JSON report
to stdout describing whether the plant is shippable. It checks:

1. Required CSVs exist under ``kb/08_Logs_Data/`` with the exact headers
   documented in DEMO_BUILD_HANDOFF.md and at least one data row.
2. Forbidden source-plant identifiers (``MMC_P7``, ``Plant 7``,
   ``plant7``, ``P7-L``) do not appear anywhere in the plant's CSVs or
   markdown for any plant other than plant7 itself.
3. (Task 13) Enterprise cross-link integrity: every line referenced in
   ``enterprise/supply-chain/data/bom_where_used.csv`` for this plant
   exists in the profile; for cloned plants there is at least one
   ``BRK-CAL-XYZ`` / ``Acme Brakes`` row.

Return code: 0 on status==ok, 1 on status==error.
JSON shape: ``{"status": "ok"|"error", "plant_id": "...", "errors": [
  {"code": "...", "path": "...", "message": "..."}
]}``
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_plant.py"


INCIDENT_HEADER = (
    "Incident_ID,Date,Time,Shift,Location,Area,Incident_Type,Severity,"
    "Description,Immediate_Cause,Root_Cause,Injury_Type,Body_Part,"
    "Treatment,Days_Away,Days_Restricted,Reported_By,Investigated_By,"
    "CAPA_ID,CAPA_Status,Closed_Date"
)
PM_HEADER = (
    "PM_ID,Asset_ID,Equipment_Name,Location,PM_Type,Frequency,"
    "Scheduled_Date,Completed_Date,Status,Technician,Duration_Hours,"
    "LOTO_Required,Findings,Follow_Up_WO,Notes"
)
TRAINING_HEADER = (
    "Training_ID,Employee_ID,Employee_Name,Department,Area,"
    "Training_Course,Training_Type,Course_Category,Scheduled_Date,"
    "Completed_Date,Status,Trainer,Score_Percent,Pass_Fail,"
    "Expiration_Date,Notes"
)


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


def _write_profile(plant_dir: Path, plant_id: str = "plant4") -> None:
    plant_dir.mkdir(parents=True, exist_ok=True)
    profile = {
        "plant_id": plant_id,
        "plant_code": "MMC_P4",
        "display_name": "Plant 4 - Monterrey",
        "location": {"city": "Monterrey", "state": "NL", "country": "MX"},
        "lines": [
            {"id": "L1", "name": "Brake-Caliper Assembly", "equipment_prefix": "P4-L1"},
            {"id": "L2", "name": "Robotic Cell", "equipment_prefix": "P4-L2"},
            {"id": "L3", "name": "Conveyor & QC", "equipment_prefix": "P4-L3"},
        ],
        "standards": ["NOM-STPS"],
        "kb": {"kb_id_env": "FOUNDRY_KB_PLANT4_ID"},
    }
    (plant_dir / "profile.yaml").write_text(
        yaml.safe_dump(profile, sort_keys=False), encoding="utf-8"
    )


def _write_csv(path: Path, header: str, row: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n" + row + "\n", encoding="utf-8")


def _write_good_plant4(plant_dir: Path) -> None:
    _write_profile(plant_dir)
    logs = plant_dir / "kb" / "08_Logs_Data"
    _write_csv(
        logs / "MMC_P4_Incident_Log.csv",
        INCIDENT_HEADER,
        "INC-P4-001,2026-01-15,08:00,A,Line L1,Press,Near-miss,Low,Loose bolt,"
        "Equipment wear,Bolt fatigue,None,N/A,N/A,0,0,J.Garza,M.Lopez,"
        "CAPA-P4-001,Open,",
    )
    _write_csv(
        logs / "MMC_P4_PM_Schedule.csv",
        PM_HEADER,
        "PM-P4-001,P4-L1-CMM-04,Brake CMM,Line L1,Quarterly,90,"
        "2026-03-01,,Scheduled,J.Reyes,2.0,Y,,WO-P4-100,Routine PM",
    )
    _write_csv(
        logs / "MMC_P4_Training_Log.csv",
        TRAINING_HEADER,
        "TRN-P4-001,EMP-P4-100,Maria Lopez,Production,L1,LOTO Refresh,"
        "Compliance,Safety,2026-02-01,2026-02-01,Completed,A.Diaz,92,Pass,"
        "2027-02-01,",
    )


def test_validate_plant_ok_on_clean_plant4(tmp_path: Path) -> None:
    """A correctly cloned Plant 4 returns status=ok and exit 0."""
    plant_dir = tmp_path / "plants" / "plant4"
    _write_good_plant4(plant_dir)

    result = _run([str(plant_dir)])

    assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"
    report = json.loads(result.stdout)
    assert report["status"] == "ok"
    assert report["plant_id"] == "plant4"
    assert report["errors"] == []


def test_validate_plant_rejects_plant7_equipment_id_remnant(tmp_path: Path) -> None:
    """A leaked P7-L1-CMM-04 in a CSV fails with forbidden_source_plant_id."""
    plant_dir = tmp_path / "plants" / "plant4"
    _write_good_plant4(plant_dir)
    pm_csv = plant_dir / "kb" / "08_Logs_Data" / "MMC_P4_PM_Schedule.csv"
    text = pm_csv.read_text(encoding="utf-8")
    pm_csv.write_text(text.replace("P4-L1-CMM-04", "P7-L1-CMM-04"), encoding="utf-8")

    result = _run([str(plant_dir)])

    assert result.returncode != 0, f"validator must exit nonzero on remnant; stdout={result.stdout}"
    report = json.loads(result.stdout)
    assert report["status"] == "error"
    assert report["plant_id"] == "plant4"
    codes = [e["code"] for e in report["errors"]]
    assert "forbidden_source_plant_id" in codes, f"expected forbidden_source_plant_id in {codes}"
    offending = next(e for e in report["errors"] if e["code"] == "forbidden_source_plant_id")
    assert "MMC_P4_PM_Schedule.csv" in offending["path"]
