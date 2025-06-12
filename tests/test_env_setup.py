import os
import shutil
import tempfile
import json
from pathlib import Path
from typing import Dict

from edamorph.env_setup import (
    get_env_paths,
    ensure_env_root_and_settings,
    load_settings,
    update_settings,
    create_runtime_dirs
)


def test_get_env_paths_creates_correct_structure():
    paths = get_env_paths()
    assert isinstance(paths, dict)
    assert all(key in paths for key in [
        "root", "settings_file", "logs", "cache", "temp", "database", "db_file"])
    assert all(isinstance(val, Path) for val in paths.values())


def test_ensure_env_root_and_settings_creates_default_files(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    paths = ensure_env_root_and_settings()

    assert paths["root"].exists()
    assert paths["settings_file"].exists()

    with open(paths["settings_file"], "r") as f:
        config = json.load(f)

    # 🛠 FIX: These must match your actual config layout
    assert config["duckdb_mode"] == "memory"
    assert "memory_temp_directory" in config
    assert "persistent_db_file_path" in config


def test_load_settings_reads_correct_data(tmp_path):
    settings_file = tmp_path / "settings.json"
    test_data = {"duckdb": {"duckdb_mode": "persistent"}}
    with open(settings_file, "w") as f:
        json.dump(test_data, f)

    result = load_settings(settings_file)
    assert result["duckdb"]["duckdb_mode"] == "persistent"


def test_update_settings_merges_dict_values(tmp_path):
    settings_file = tmp_path / "settings.json"
    initial = {"duckdb": {"duckdb_mode": "memory", "a": 1}}
    with open(settings_file, "w") as f:
        json.dump(initial, f)

    update_settings(settings_file, {"duckdb": {"a": 2, "b": 3}})
    result = load_settings(settings_file)

    assert result["duckdb"]["a"] == 2
    assert result["duckdb"]["b"] == 3
    assert result["duckdb"]["duckdb_mode"] == "memory"


def test_update_settings_overwrites_non_dict():
    with tempfile.TemporaryDirectory() as tmp:
        settings_file = Path(tmp) / "settings.json"
        with open(settings_file, "w") as f:
            json.dump({"version": "1.0.0"}, f)

        update_settings(settings_file, {"version": "2.0.0"})
        result = load_settings(settings_file)
        assert result["version"] == "2.0.0"


def test_create_runtime_dirs_creates_correct_paths(tmp_path):
    paths = {
        "logs": tmp_path / "logs",
        "cache": tmp_path / "cache",
        "temp": tmp_path / "temp",
        "database": tmp_path / "db",
        "db_file": tmp_path / "db" / "edamorph.db"
    }

    config = {
        "duckdb": {
            "duckdb_mode": "memory",
            "memory_temp_directory": str(paths["temp"]),
            "persistent_db_file_path": str(paths["db_file"])
        }
    }

    create_runtime_dirs(config, paths)

    assert paths["logs"].exists()
    assert paths["cache"].exists()
    assert paths["temp"].exists()

    config["duckdb"]["duckdb_mode"] = "persistent"
    create_runtime_dirs(config, paths)
    assert paths["database"].exists()

def test_update_settings_adds_new_key(tmp_path):
    settings_file = tmp_path / "settings.json"
    with open(settings_file, "w") as f:
        json.dump({}, f)

    update_settings(settings_file, {"new_section": {"key": "value"}})
    result = load_settings(settings_file)
    assert "new_section" in result
    assert result["new_section"]["key"] == "value"

def test_ensure_env_root_and_settings_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    first = ensure_env_root_and_settings()
    second = ensure_env_root_and_settings()

    assert first["settings_file"].read_text() == second["settings_file"].read_text()

def test_create_runtime_dirs_with_unknown_mode(tmp_path):
    paths = {
        "logs": tmp_path / "logs",
        "cache": tmp_path / "cache",
        "temp": tmp_path / "temp",
        "database": tmp_path / "db",
        "db_file": tmp_path / "db" / "edamorph.db"
    }

    config = {"duckdb": {"duckdb_mode": "invalid_mode"}}
    create_runtime_dirs(config, paths)

    # logs/cache should still be created even if mode is wrong
    assert paths["logs"].exists()
    assert paths["cache"].exists()