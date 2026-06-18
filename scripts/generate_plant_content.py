"""Plant content generator (Gate D Task 8).

Mechanical phase: scrubs plant-local identifiers from CSVs under
``plants/<plant>/kb/08_Logs_Data/`` and applies deterministic jitter to
date and numeric-quantity columns. The narrative LLM regeneration phase
arrives in Task 9.

CLI:
    python scripts/generate_plant_content.py --plant plant4 --mechanical-only

Substitutions (applied globally to each CSV body; header is preserved
byte-for-byte because none of these patterns appear in the schema row):

* ``MMC_P7``        -> ``MMC_<plant_code>``
* ``PM-P7-``        -> ``PM-<plant_code>-``
* ``INC-P7-``       -> ``INC-<plant_code>-``
* ``TRN-P7-``       -> ``TRN-<plant_code>-``
* ``P7-L<n>-...``   -> ``<plant_code>-L<n>-...``

Cross-plant shared scenario IDs (``BRK-CAL-XYZ``, ``Acme Brakes``, etc.)
are NOT mutated; the regex set above is intentionally narrow.

Jitter seed: ``sha256(f"{plant_id}:{filename}:{row_index}")``. Same seed
on every run, so output is byte-deterministic.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Sequence

import yaml

_DATE_VALUE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_QTY_HEADER_KEYWORDS: tuple[str, ...] = (
    "hours",
    "duration",
    "qty",
    "quantity",
    "score",
    "volume",
)


def derive_plant_code(profile: dict, plant_id: str) -> str:
    """Return profile['plant_code'] if present, else derive from plant_id."""
    code = profile.get("plant_code")
    if code:
        return str(code)
    suffix = plant_id[len("plant"):]
    return f"P{suffix.upper()}"


def build_substitutions(plant_code: str) -> list[tuple[re.Pattern[str], str]]:
    """Ordered (pattern, replacement) pairs scrubbing P7 -> plant_code tokens.

    Deliberately narrow: only well-known work-order/equipment prefixes are
    rewritten so cross-plant scenario IDs (BRK-CAL-XYZ, Acme Brakes, etc.)
    are never touched.
    """
    return [
        (re.compile(r"MMC_P7"), f"MMC_{plant_code}"),
        (re.compile(r"\bPM-P7-"), f"PM-{plant_code}-"),
        (re.compile(r"\bINC-P7-"), f"INC-{plant_code}-"),
        (re.compile(r"\bTRN-P7-"), f"TRN-{plant_code}-"),
        # Equipment IDs like P7-L1-CMM-04, P7-L2-ROB-001
        (re.compile(r"\bP7-L(\d)-"), rf"{plant_code}-L\1-"),
    ]


def _row_seed(plant_id: str, filename: str, row_index: int) -> int:
    """Deterministic per-row seed used for date + quantity jitter."""
    digest = hashlib.sha256(
        f"{plant_id}:{filename}:{row_index}".encode("utf-8")
    ).hexdigest()
    return int(digest[:16], 16)


def jitter_date(value: str, seed: int) -> str:
    """Shift an ISO date by a deterministic offset in [-3, +3] days."""
    if not _DATE_VALUE_RE.match(value):
        return value
    try:
        d = date.fromisoformat(value)
    except ValueError:
        return value
    offset = (seed % 7) - 3
    return (d + timedelta(days=offset)).isoformat()


def jitter_numeric(value: str, seed: int) -> str:
    """Scale a numeric value by a deterministic factor in [-5%, +5%].

    Preserves the source's decimal precision so "2.0" stays "2.1", "92"
    stays an integer "93", etc.
    """
    try:
        n = float(value)
    except ValueError:
        return value
    factor = 1.0 + (((seed >> 16) % 11) - 5) / 100.0
    new = n * factor
    if "." in value:
        decimals = len(value.split(".", 1)[1])
        return f"{new:.{decimals}f}"
    return str(int(round(new)))


def _is_date_header(name: str) -> bool:
    return "date" in name.lower()


def _is_quantity_header(name: str) -> bool:
    n = name.lower()
    return any(k in n for k in _QTY_HEADER_KEYWORDS)


def process_csv(path: Path, plant_id: str, plant_code: str) -> None:
    """Apply substitutions + per-row jitter to a CSV in place."""
    subs = build_substitutions(plant_code)
    raw = path.read_text(encoding="utf-8")
    for pat, repl in subs:
        raw = pat.sub(repl, raw)

    reader = csv.reader(io.StringIO(raw))
    rows = list(reader)
    if not rows:
        return
    header = rows[0]
    out_rows: list[list[str]] = [header]
    for row_index, row in enumerate(rows[1:]):
        seed = _row_seed(plant_id, path.name, row_index)
        new_row: list[str] = []
        for col_idx, cell in enumerate(row):
            col_name = header[col_idx] if col_idx < len(header) else ""
            if _is_date_header(col_name):
                new_row.append(jitter_date(cell, seed))
            elif _is_quantity_header(col_name):
                new_row.append(jitter_numeric(cell, seed))
            else:
                new_row.append(cell)
        out_rows.append(new_row)

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    for r in out_rows:
        writer.writerow(r)
    path.write_text(buf.getvalue(), encoding="utf-8")


def run_mechanical_phase(plant_dir: Path, plant_id: str, plant_code: str) -> int:
    csv_dir = plant_dir / "kb" / "08_Logs_Data"
    if not csv_dir.is_dir():
        return 0
    count = 0
    for csv_path in sorted(csv_dir.glob("*.csv")):
        process_csv(csv_path, plant_id, plant_code)
        count += 1
    return count


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="generate_plant_content",
        description=(
            "Generate plant-specific content for a cloned plant: mechanical "
            "CSV substitutions + deterministic jitter, plus (in Task 9) LLM "
            "narrative regeneration."
        ),
    )
    p.add_argument("--plant", required=True, help="plant_id (e.g. plant4)")
    p.add_argument(
        "--plants-root",
        type=Path,
        default=Path("plants"),
        help="root containing per-plant subdirectories (default: plants)",
    )
    p.add_argument(
        "--enterprise-root",
        type=Path,
        default=Path("enterprise"),
        help="root containing enterprise CSVs (default: enterprise)",
    )
    p.add_argument(
        "--mechanical-only",
        action="store_true",
        help="skip the LLM narrative regeneration phase (Task 9)",
    )
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    plant_dir = args.plants_root / args.plant
    profile_path = plant_dir / "profile.yaml"
    if not profile_path.is_file():
        print(f"plant profile not found: {profile_path}", file=sys.stderr)
        return 1
    try:
        profile = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"failed to parse profile YAML: {exc}", file=sys.stderr)
        return 1
    if not isinstance(profile, dict):
        print("profile must be a YAML mapping", file=sys.stderr)
        return 1

    plant_code = derive_plant_code(profile, args.plant)
    n = run_mechanical_phase(plant_dir, args.plant, plant_code)
    print(f"mechanical: processed {n} CSV file(s) for {args.plant} ({plant_code})")

    if args.mechanical_only:
        return 0

    # Narrative LLM phase implemented in Task 9.
    print("(narrative phase will be implemented in Task 9)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
