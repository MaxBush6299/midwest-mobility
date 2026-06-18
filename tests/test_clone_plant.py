"""Tests for scripts/clone_plant.py (Gate D Task 5).

These tests define the contract for the plant cloning CLI BEFORE the
script exists (TDD red phase). They use a self-contained mini template
under tmp_path so they don't depend on the full templates/plant_template
shape — that integration is exercised in later tasks.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "clone_plant.py"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Invoke clone_plant.py with UTF-8 stdio, capturing stdout/stderr as text."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


@pytest.fixture
def mini_template(tmp_path: Path) -> Path:
    """Minimal valid template directory exercising filename + content substitution."""
    tpl = tmp_path / "template"
    (tpl / "kb" / "02_EHS_Internal").mkdir(parents=True)
    (tpl / "profile.yaml.j2").write_text(
        "plant_id: {{ plant_id }}\n"
        "plant_code: {{ plant_code }}\n"
        "display_name: {{ display_name }}\n",
        encoding="utf-8",
    )
    # Filename substitution AND content substitution AND plant_name derivation
    (tpl / "kb" / "02_EHS_Internal" / "MMC_{{ plant_code }}_Doc.md.j2").write_text(
        "# MMC {{ plant_name }} - Doc\n\n"
        "Line prefix: {{ plant_code }}-L1\n"
        "KB env: {{ kb_id_env }}\n",
        encoding="utf-8",
    )
    return tpl


def _write_profile(path: Path, **overrides) -> Path:
    profile = {
        "plant_id": "plantx",
        "plant_code": "PX",
        "plant_name": "Plant X",
        "display_name": "MMC Plant X (Testville)",
        "lines": [
            {"id": "L1", "name": "Test Line", "equipment_prefix": "L1-TST-"},
        ],
        "agents": [],
        "kb": {"kb_id_env": "FOUNDRY_IQ_KB_PLANTX_ID"},
    }
    profile.update(overrides)
    path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    return path


@pytest.fixture
def plantx_profile(tmp_path: Path) -> Path:
    return _write_profile(tmp_path / "plantx.profile.yaml")


def test_render_produces_expected_files(
    mini_template: Path, plantx_profile: Path, tmp_path: Path
) -> None:
    """Happy path: renders profile.yaml + MMC_PX_Doc.md with substitutions applied."""
    out = tmp_path / "out"
    result = _run([
        "--profile", str(plantx_profile),
        "--template", str(mini_template),
        "--output-root", str(out),
    ])
    assert result.returncode == 0, (
        f"clone failed:\nstderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    )

    plant_dir = out / "plantx"
    assert (plant_dir / "profile.yaml").is_file()
    assert (plant_dir / "kb" / "02_EHS_Internal" / "MMC_PX_Doc.md").is_file()
    # No .j2 leftovers - extension must be stripped during render
    assert not list(plant_dir.rglob("*.j2")), "found unrendered .j2 files"

    profile_text = (plant_dir / "profile.yaml").read_text(encoding="utf-8")
    assert "plant_id: plantx" in profile_text
    assert "plant_code: PX" in profile_text
    assert "MMC Plant X (Testville)" in profile_text

    doc_text = (plant_dir / "kb" / "02_EHS_Internal" / "MMC_PX_Doc.md").read_text(
        encoding="utf-8"
    )
    assert "MMC Plant X - Doc" in doc_text
    assert "PX-L1" in doc_text
    assert "FOUNDRY_IQ_KB_PLANTX_ID" in doc_text
    assert "{{" not in doc_text  # no unrendered Jinja


def test_refuses_to_overwrite_without_force(
    mini_template: Path, plantx_profile: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    (out / "plantx").mkdir(parents=True)
    sentinel = out / "plantx" / "sentinel.txt"
    sentinel.write_text("preexisting", encoding="utf-8")

    result = _run([
        "--profile", str(plantx_profile),
        "--template", str(mini_template),
        "--output-root", str(out),
    ])
    assert result.returncode != 0, "expected nonzero exit when output dir exists"
    assert "Refusing to overwrite" in result.stderr
    assert sentinel.read_text(encoding="utf-8") == "preexisting", (
        "pre-existing files must not be touched on refusal"
    )


def test_force_overwrites_existing_plant(
    mini_template: Path, plantx_profile: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    (out / "plantx").mkdir(parents=True)
    (out / "plantx" / "stale.txt").write_text("stale", encoding="utf-8")

    result = _run([
        "--profile", str(plantx_profile),
        "--template", str(mini_template),
        "--output-root", str(out),
        "--force",
    ])
    assert result.returncode == 0, (
        f"--force clone failed:\nstderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    )
    assert (out / "plantx" / "profile.yaml").is_file()


def test_rejects_invalid_plant_id(mini_template: Path, tmp_path: Path) -> None:
    """plant_id must match plant<n>; 'factory-7' is invalid."""
    bad = _write_profile(tmp_path / "bad.profile.yaml", plant_id="factory-7")
    result = _run([
        "--profile", str(bad),
        "--template", str(mini_template),
        "--output-root", str(tmp_path / "out"),
    ])
    assert result.returncode != 0
    assert "plant_id" in result.stderr.lower(), (
        f"expected plant_id error in stderr; got:\n{result.stderr}"
    )


def test_rejects_missing_required_keys(mini_template: Path, tmp_path: Path) -> None:
    """Profiles missing required keys (display_name, lines, agents, kb) are rejected."""
    incomplete = {"plant_id": "plantx", "plant_code": "PX"}
    p = tmp_path / "incomplete.profile.yaml"
    p.write_text(yaml.safe_dump(incomplete, sort_keys=False), encoding="utf-8")
    result = _run([
        "--profile", str(p),
        "--template", str(mini_template),
        "--output-root", str(tmp_path / "out"),
    ])
    assert result.returncode != 0
    stderr_low = result.stderr.lower()
    assert "missing" in stderr_low or "required" in stderr_low, (
        f"expected missing/required error; got:\n{result.stderr}"
    )


def test_help_lists_all_flags() -> None:
    """--help must document every supported flag."""
    result = _run(["--help"])
    assert result.returncode == 0, f"help failed: stderr=\n{result.stderr}"
    for flag in ("--profile", "--template", "--output-root", "--force"):
        assert flag in result.stdout, f"missing {flag} in --help output"
