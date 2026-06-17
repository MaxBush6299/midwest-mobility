"""Gate B Task 2 — ensure no `TODO(verify-on-Learn)` / `TODO(verify)` markers remain."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_verify_markers_remain():
    offenders: list[str] = []
    for base in [ROOT / "infra" / "bicep", ROOT / "src" / "mmc_agents", ROOT / "scripts"]:
        for path in base.rglob("*"):
            if path.suffix in {".py", ".bicep", ".bicepparam"}:
                text = path.read_text(encoding="utf-8")
                if "TODO(verify-on-Learn)" in text or "TODO(verify)" in text:
                    offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], f"Unresolved verification markers in: {offenders}"
