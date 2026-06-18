"""Contract tests for templates/plant_template/ (Gate D Task 4).

Locks the *shape* of the canonical plant template so future clones
(Plant 4, Plant 5, ...) and any refactors cannot silently drift away
from the agreed structure documented in
docs/specs/gate-d-template-map.md.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "templates" / "plant_template"
CSV_DIR = TEMPLATE_ROOT / "kb" / "08_Logs_Data"

REQUIRED_CSV_TEMPLATES = (
    "MMC_{{ plant_code }}_Incident_Log.csv.j2",
    "MMC_{{ plant_code }}_PM_Schedule.csv.j2",
    "MMC_{{ plant_code }}_Training_Log.csv.j2",
)


@pytest.mark.parametrize("name", REQUIRED_CSV_TEMPLATES)
def test_required_csv_template_exists(name: str) -> None:
    path = CSV_DIR / name
    assert path.is_file(), f"missing CSV template: {path.relative_to(ROOT)}"


@pytest.mark.parametrize("name", REQUIRED_CSV_TEMPLATES)
def test_csv_template_has_nonempty_header(name: str) -> None:
    path = CSV_DIR / name
    if not path.is_file():
        pytest.skip(f"{name} not yet created; covered by existence test")
    first_line = path.read_text(encoding="utf-8").splitlines()[0]
    assert first_line.strip(), f"{name} has empty header row"
    # CSV header must not have been accidentally templated; column names are
    # part of the SQL/Foundry contract and must be byte-identical across plants.
    assert "{{" not in first_line, (
        f"{name} header contains Jinja substitution; headers must be literal"
    )


def test_no_agent_json_templates() -> None:
    """Agent definitions are LLM-generated at clone time, never templated.

    Per gate-d-template-map.md Decision A4: per-plant agents render from the
    profile via agent_factory; there must be no static agent JSON templates.
    """
    agents_dir = TEMPLATE_ROOT / "agents"
    if not agents_dir.exists():
        return
    strays = sorted(agents_dir.rglob("*.agent.json.j2"))
    assert not strays, (
        "templates/plant_template/agents/ must not contain *.agent.json.j2 "
        f"templates; found: {[p.relative_to(ROOT).as_posix() for p in strays]}"
    )
