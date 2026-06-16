# tests/test_fixtures_loader.py
from pathlib import Path
import json, pytest
from mmc_agents.tools.fixtures_loader import load_fixture

def test_load_existing_key(tmp_path: Path):
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"K1": {"a": 1}, "K2": {"a": 2}}))
    assert load_fixture(p, "K1") == {"a": 1}

def test_missing_key_returns_none(tmp_path: Path):
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"K1": {"a": 1}}))
    assert load_fixture(p, "NOPE") is None

def test_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_fixture(tmp_path / "missing.json", "K1")
