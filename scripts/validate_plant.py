"""Validate a cloned plant directory (Gate D Task 12, 13).

Checks that a plant directory under ``plants/<plant_id>/`` is shippable:

1. ``profile.yaml`` exists and parses.
2. The three required CSVs exist under ``kb/08_Logs_Data/`` with the
   exact headers documented in ``DEMO_BUILD_HANDOFF.md`` and at least
   one data row each.
3. For any plant other than ``plant7``, no source-plant identifier
   (``MMC_P7``, ``Plant 7``, ``plant7``, ``P7-L<n>-...``) appears in
   the plant's CSVs or markdown.
4. Any ``P<n>-L<n>-...`` local identifier embedded in the plant matches
   the current plant's letter+digit code (e.g. Plant 4 must use ``P4-``).
5. (Task 13) Enterprise cross-link sanity for the BOM where-used table.

Output: a JSON object on stdout with shape::

    {
      "status": "ok" | "error",
      "plant_id": "...",
      "errors": [
        {"code": "...", "path": "...", "message": "..."}
      ]
    }

Exit code: 0 on ``status == ok``, 1 on ``status == error``.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Sequence

import yaml


# Exact headers from DEMO_BUILD_HANDOFF.md (do NOT alter without also
# updating the handoff doc and the templates under templates/plant_template/).
REQUIRED_CSVS: dict[str, tuple[str, ...]] = {
    "MMC_{code}_Incident_Log.csv": (
        "Incident_ID", "Date", "Time", "Shift", "Location", "Area",
        "Incident_Type", "Severity", "Description", "Immediate_Cause",
        "Root_Cause", "Injury_Type", "Body_Part", "Treatment", "Days_Away",
        "Days_Restricted", "Reported_By", "Investigated_By", "CAPA_ID",
        "CAPA_Status", "Closed_Date",
    ),
    "MMC_{code}_PM_Schedule.csv": (
        "PM_ID", "Asset_ID", "Equipment_Name", "Location", "PM_Type",
        "Frequency", "Scheduled_Date", "Completed_Date", "Status",
        "Technician", "Duration_Hours", "LOTO_Required", "Findings",
        "Follow_Up_WO", "Notes",
    ),
    "MMC_{code}_Training_Log.csv": (
        "Training_ID", "Employee_ID", "Employee_Name", "Department", "Area",
        "Training_Course", "Training_Type", "Course_Category",
        "Scheduled_Date", "Completed_Date", "Status", "Trainer",
        "Score_Percent", "Pass_Fail", "Expiration_Date", "Notes",
    ),
}

# Forbidden source-plant identifiers (applied to non-plant7 plants only).
_FORBIDDEN_RE = re.compile(r"MMC_P7|Plant 7|plant7|P7-L\d")

# Local equipment ID pattern: P<n+>-L<n>-<...>
_LOCAL_EQUIP_RE = re.compile(r"\bP[A-Z0-9]+-L\d+-[A-Z0-9]+-\d+\b")
_LOCAL_PREFIX_RE = re.compile(r"^P[A-Z0-9]+-")


def _short_code(plant_code: str) -> str:
    """MMC_P4 -> P4."""
    m = re.search(r"P([A-Z0-9]+)$", plant_code)
    return f"P{m.group(1)}" if m else ""


def _scan_text(text: str, plant_id: str, short: str) -> list[str]:
    """Return (code, snippet) issues for one text blob. Caller adds path."""
    issues: list[tuple[str, str]] = []
    if plant_id != "plant7":
        for m in _FORBIDDEN_RE.finditer(text):
            issues.append(("forbidden_source_plant_id", m.group(0)))
    if short:
        for m in _LOCAL_EQUIP_RE.finditer(text):
            tok = m.group(0)
            prefix = _LOCAL_PREFIX_RE.match(tok).group(0).rstrip("-")
            if prefix != short:
                issues.append(("mismatched_local_id", tok))
    return [f"{code}:{snip}" for code, snip in issues]


def _validate_csv(
    path: Path,
    expected_header: Sequence[str],
    plant_id: str,
    short: str,
    errors: list[dict],
) -> None:
    rel = path.name
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append({"code": "missing_csv", "path": rel, "message": str(exc)})
        return
    rows = list(csv.reader(text.splitlines()))
    if not rows:
        errors.append({"code": "empty_csv", "path": rel, "message": "file has no rows"})
        return
    header = rows[0]
    if tuple(header) != tuple(expected_header):
        errors.append({
            "code": "bad_csv_header",
            "path": rel,
            "message": f"header mismatch; expected {len(expected_header)} columns, got {len(header)}",
        })
        return
    data_rows = [r for r in rows[1:] if any(c.strip() for c in r)]
    if not data_rows:
        errors.append({
            "code": "empty_csv",
            "path": rel,
            "message": "header present but no data rows",
        })
    for tagged in _scan_text(text, plant_id, short):
        code, snippet = tagged.split(":", 1)
        errors.append({
            "code": code,
            "path": rel,
            "message": f"found '{snippet}' in CSV",
        })


def _validate_markdown(
    plant_dir: Path, plant_id: str, short: str, errors: list[dict]
) -> None:
    kb_dir = plant_dir / "kb"
    if not kb_dir.is_dir():
        return
    for md_path in sorted(kb_dir.rglob("*.md")):
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = str(md_path.relative_to(plant_dir))
        for tagged in _scan_text(text, plant_id, short):
            code, snippet = tagged.split(":", 1)
            errors.append({
                "code": code,
                "path": rel,
                "message": f"found '{snippet}' in markdown",
            })


def _validate_enterprise_bom(
    bom_path: Path,
    plant_id: str,
    profile: dict,
    errors: list[dict],
) -> None:
    """Task 13 cross-link checks. No-op if BOM file is missing."""
    if not bom_path.is_file():
        return
    line_ids = {ln.get("id") for ln in (profile.get("lines") or []) if ln.get("id")}
    try:
        rows = list(csv.DictReader(bom_path.read_text(encoding="utf-8").splitlines()))
    except OSError as exc:
        errors.append({
            "code": "missing_bom",
            "path": str(bom_path),
            "message": str(exc),
        })
        return

    plant_rows = [r for r in rows if r.get("Plant_ID") == plant_id]
    for r in plant_rows:
        line = r.get("Line_ID")
        if line and line not in line_ids:
            errors.append({
                "code": "bad_cross_link",
                "path": str(bom_path),
                "message": (
                    f"bom references {plant_id} {line} but profile lines "
                    f"are {sorted(line_ids)}"
                ),
            })

    if plant_id != "plant7":
        # For cloned plants, the BRK-CAL-XYZ / Acme Brakes cross-plant
        # scenario row must be present.
        has_link = any(
            r.get("Part_ID") == "BRK-CAL-XYZ"
            and r.get("Part_Name") == "Brake Caliper Assembly"
            and r.get("Plant_ID") == plant_id
            for r in rows
        )
        if not has_link:
            errors.append({
                "code": "missing_brake_caliper_cross_link",
                "path": str(bom_path),
                "message": (
                    f"no BRK-CAL-XYZ row for {plant_id}; run "
                    "generate_plant_content.py to populate the cross-plant link"
                ),
            })


def validate_plant(plant_dir: Path, enterprise_root: Path) -> dict:
    errors: list[dict] = []
    plant_id = plant_dir.name
    report: dict = {"status": "ok", "plant_id": plant_id, "errors": errors}

    profile_path = plant_dir / "profile.yaml"
    if not profile_path.is_file():
        errors.append({
            "code": "missing_profile",
            "path": "profile.yaml",
            "message": f"{profile_path} not found",
        })
        report["status"] = "error"
        return report
    try:
        profile = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        errors.append({
            "code": "bad_profile",
            "path": "profile.yaml",
            "message": str(exc),
        })
        report["status"] = "error"
        return report
    if not isinstance(profile, dict):
        errors.append({
            "code": "bad_profile",
            "path": "profile.yaml",
            "message": "profile must be a YAML mapping",
        })
        report["status"] = "error"
        return report

    plant_id = profile.get("plant_id") or plant_id
    report["plant_id"] = plant_id
    plant_code = profile.get("plant_code") or ""
    short = _short_code(plant_code)

    logs_dir = plant_dir / "kb" / "08_Logs_Data"
    for template_name, header in REQUIRED_CSVS.items():
        csv_name = template_name.format(code=short)
        _validate_csv(logs_dir / csv_name, header, plant_id, short, errors)

    _validate_markdown(plant_dir, plant_id, short, errors)

    bom_path = enterprise_root / "supply-chain" / "data" / "bom_where_used.csv"
    _validate_enterprise_bom(bom_path, plant_id, profile, errors)

    report["status"] = "error" if errors else "ok"
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("plant_dir", type=Path, help="path to plants/<plant_id>/")
    p.add_argument(
        "--enterprise-root",
        type=Path,
        default=Path("enterprise"),
        help="root containing enterprise CSVs (default: enterprise)",
    )
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    report = validate_plant(args.plant_dir, args.enterprise_root)
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
