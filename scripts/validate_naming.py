"""Plant 7 naming + standards validator (Gate B Task 3).

Rules:
- Plant codes: only MMC_P7 is accepted (other MMC_P\\d+ tokens are errors).
- Line IDs: only L1, L2, L3 are accepted.
- Part IDs: must match XXX-XXXX-XXXX style (3 letters, then 2-4 alnum, then 2-4 alnum).
- Equipment IDs: must match L[123]-(PRS|ROB|CNV)-\\d{3}.

CLI: `python -m scripts.validate_naming <path>...` walks each path, validates
*.md, *.csv, *.json, *.yaml text content, and exits 1 if any errors are found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

VALID_LINES = {"L1", "L2", "L3"}
_PART_RE = re.compile(r"^[A-Z]{3}-[A-Z0-9]{2,4}-[A-Z0-9]{2,4}$")
_EQUIP_RE = re.compile(r"^L[123]-(PRS|ROB|CNV)-\d{3}$")
_PLANT_TOKEN_RE = re.compile(r"MMC_P\d+")
_LINE_TOKEN_RE = re.compile(r"\bL\d+\b")
_VALID_SUFFIXES = {".md", ".csv", ".json", ".yaml", ".yml", ".txt"}


def validate_part_id(value: str) -> list[str]:
    return [] if _PART_RE.match(value) else [value]


def validate_equipment_id(value: str) -> list[str]:
    return [] if _EQUIP_RE.match(value) else [value]


def validate_text(text: str) -> list[str]:
    errors: list[str] = []
    errors += [p for p in _PLANT_TOKEN_RE.findall(text) if p != "MMC_P7"]
    errors += [l for l in _LINE_TOKEN_RE.findall(text) if l not in VALID_LINES]
    return errors


def _iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for p in paths:
        if p.is_dir():
            for child in p.rglob("*"):
                if child.is_file() and child.suffix.lower() in _VALID_SUFFIXES:
                    yield child
        elif p.is_file():
            yield p


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: validate_naming.py <path> [path ...]", file=sys.stderr)
        return 2
    paths = [Path(a) for a in argv]
    total_errors = 0
    for f in _iter_files(paths):
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        errs = validate_text(text)
        if errs:
            total_errors += len(errs)
            print(f"{f}: {errs}")
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
