"""Tests for scripts/generate_plant_content.py (Gate D Tasks 7, 9).

Defines the contract for the plant content generator. The generator has
two phases:

1. *Mechanical* substitution of plant-local CSV identifiers (P7-Lx-* to
   P4-Lx-*, PM-P7- to PM-P4-, etc.) plus deterministic jitter on dates
   and quantities seeded from sha256(plant_id:filename:row_index).
2. *Narrative* LLM regeneration of KB markdown (Task 9). Tests use a
   FakeChatClient stub so no live Azure dependency is required.

Mechanical tests use ``--mechanical-only`` via subprocess; narrative
tests import the script's functions directly and inject the fake
client.
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
sys.path.insert(0, str(ROOT))

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


# ---------------------------------------------------------------------------
# Task 9: narrative LLM regeneration (in-process, fake chat client)
# ---------------------------------------------------------------------------


class FakeChatClient:
    """Test double for an LLM chat client supporting .complete(prompt)."""

    def __init__(self, response_text: str = "") -> None:
        self.response_text = response_text
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response_text


class InvokeOnlyClient:
    """Test double exposing only .invoke(prompt) — exercises fallback path."""

    def __init__(self, response_text: str = "") -> None:
        self.response_text = response_text
        self.prompts: list[str] = []

    def invoke(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response_text


def _plant4_profile() -> dict:
    return {
        "plant_id": "plant4",
        "plant_code": "P4",
        "display_name": "MMC Plant 4 (Monterrey)",
        "location": {"city": "Monterrey", "state": "NL", "country": "MX"},
        "lines": [
            {"id": "L1", "name": "Brake-Caliper Assembly", "equipment_prefix": "L1-CMM-"},
            {"id": "L2", "name": "Paint and Final Finish", "equipment_prefix": "L2-PNT-"},
        ],
        "standards": ["NOM-STPS-001", "ISO-45001", "ISO-9001"],
        "agents": [],
        "kb": {"kb_id_env": "FOUNDRY_IQ_KB_PLANT4_ID"},
    }


def test_narrative_prompt_includes_source_doc_and_plant_context() -> None:
    from scripts.generate_plant_content import build_narrative_prompt

    source = (
        "# MMC Plant 7 LOTO SOP\n\n"
        "Lines 1-3 hydraulic isolation per OSHA 29 CFR 1910.147.\n"
        "Equipment: P7-L1-PRS-001.\n"
    )
    prompt = build_narrative_prompt(source, _plant4_profile())

    assert source in prompt, "prompt must include the full source doc"
    assert "Monterrey" in prompt or "MX" in prompt, "prompt must convey plant location"
    assert "Brake-Caliper Assembly" in prompt, "prompt must convey plant lines"
    # The model must be told what NOT to emit.
    assert "MMC_P7" in prompt or "Plant 7" in prompt or "plant7" in prompt, (
        "prompt must mention the source-plant tokens the model must avoid"
    )


def test_narrative_regeneration_writes_clean_plant4_text(tmp_path: Path) -> None:
    from scripts.generate_plant_content import regenerate_narrative_file

    source = tmp_path / "plant7" / "MMC_P7_LOTO_SOP.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "# MMC Plant 7 LOTO SOP\nEquipment: P7-L1-PRS-001\n", encoding="utf-8"
    )
    dest = tmp_path / "plant4" / "MMC_P4_LOTO_SOP.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("rendered placeholder", encoding="utf-8")

    fake = FakeChatClient(
        response_text=(
            "# MMC Plant 4 LOTO SOP\n\n"
            "Brake-Caliper Assembly hydraulic isolation per NOM-STPS-001.\n"
            "Equipment: P4-L1-CMM-04. Shared part: BRK-CAL-XYZ.\n"
        )
    )

    regenerate_narrative_file(source, dest, _plant4_profile(), fake)

    assert len(fake.prompts) == 1
    assert "MMC Plant 7 LOTO SOP" in fake.prompts[0]
    written = dest.read_text(encoding="utf-8")
    assert "MMC Plant 4" in written
    assert "P4-L1-CMM-04" in written
    assert "BRK-CAL-XYZ" in written
    for forbidden in ("MMC_P7", "Plant 7", "plant7", "P7-L"):
        assert forbidden not in written, f"forbidden remnant {forbidden!r} in output"


def test_narrative_raises_on_plant7_remnant(tmp_path: Path) -> None:
    from scripts.generate_plant_content import (
        NarrativeContaminationError,
        regenerate_narrative_file,
    )

    source = tmp_path / "src.md"
    source.write_text("# Source doc", encoding="utf-8")
    dest = tmp_path / "dst.md"

    # Model "leaks" a P7-L equipment ID — must be rejected and dest NOT written.
    fake = FakeChatClient(
        response_text="# Plant 4\nLeaked: P7-L1-PRS-001 still here"
    )
    with pytest.raises(NarrativeContaminationError) as exc:
        regenerate_narrative_file(source, dest, _plant4_profile(), fake)

    msg = str(exc.value)
    assert dest.name in msg or str(dest) in msg, "error must name the offending file"
    assert "P7-L" in msg or "plant7" in msg.lower() or "remnant" in msg.lower()
    assert not dest.exists(), "destination must NOT be written when contamination detected"


def test_narrative_supports_invoke_fallback(tmp_path: Path) -> None:
    """Clients with .invoke() instead of .complete() must also work."""
    from scripts.generate_plant_content import regenerate_narrative_file

    source = tmp_path / "src.md"
    source.write_text("# Source", encoding="utf-8")
    dest = tmp_path / "dst.md"

    client = InvokeOnlyClient(
        response_text="# Clean Plant 4 text\nBRK-CAL-XYZ stays.\n"
    )
    regenerate_narrative_file(source, dest, _plant4_profile(), client)

    assert len(client.prompts) == 1
    assert dest.read_text(encoding="utf-8") == client.response_text
