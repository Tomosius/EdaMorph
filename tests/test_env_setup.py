import os
import sys
import json
import tempfile
from pathlib import Path
import shutil
import pytest
from types import SimpleNamespace

# --- IMPORT MODULE UNDER TEST ---
import edamorph.env_setup as es


def test_sanitize_name():
    assert es.sanitize_name("Some Env") == "some_env"
    assert es.sanitize_name("Path/To/Foo") == "path_to_foo"


@pytest.mark.parametrize("env, exe, expected", [
    ({"CONDA_PREFIX": "/env", "CONDA_EXE": "/bin/mamba"}, None, "mamba"),
    ({"CONDA_PREFIX": "/env", "CONDA_EXE": "/bin/conda"}, None, "conda"),
    ({"CONDA_PREFIX": "/env", "CONDA_EXE": "/bin/miniconda"}, None, "miniconda"),
    ({"CONDA_PREFIX": "/env", "CONDA_EXE": "/bin/anaconda"}, None, "anaconda"),
    ({"PYENV_VERSION": "3.11.0"}, None, "pyenv"),
    ({"POETRY_ACTIVE": "1"}, None, "poetry"),
], ids=["mamba", "conda", "miniconda", "anaconda", "pyenv", "poetry"])
def test_detect_env_type(monkeypatch, env, exe, expected):
    monkeypatch.delenv("CONDA_PREFIX", raising=False)
    monkeypatch.delenv("PYENV_VERSION", raising=False)
    monkeypatch.delenv("POETRY_ACTIVE", raising=False)

    for k, v in env.items():
        monkeypatch.setenv(k, v)
    assert es.detect_env_type() == expected


def test_detect_env_name_conda(monkeypatch):
    monkeypatch.setenv("CONDA_PREFIX", "/opt/conda/envs/myenv")
    monkeypatch.setenv("CONDA_DEFAULT_ENV", "myenv")
    assert es.detect_env_name() == "myenv"


def test_detect_env_name_pyenv(monkeypatch):
    monkeypatch.setenv("PYENV_VERSION", "3.10.5")
    monkeypatch.delenv("CONDA_PREFIX", raising=False)
    monkeypatch.delenv("CONDA_DEFAULT_ENV", raising=False)
    monkeypatch.setattr(sys, "prefix", "/fake/pyenv/path/3.10.5")
    assert es.detect_env_name() == "3.10.5"


def test_detect_env_name_default(monkeypatch):
    monkeypatch.delenv("CONDA_PREFIX", raising=False)
    monkeypatch.delenv("PYENV_VERSION", raising=False)
    assert isinstance(es.detect_env_name(), str)


def test_detect_project_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert es.detect_project_name() == tmp_path.name


def test_detect_runtime_context_structure():
    result = es.detect_runtime_context()
    assert isinstance(result, tuple)
    assert len(result) == 3


def test_get_env_paths_structure():
    paths = es.get_env_paths()
    keys = ["root", "settings_file", "logs", "cache", "temp", "database", "db_file"]
    for key in keys:
        assert key in paths and isinstance(paths[key], Path)


def test_ensure_env_root_and_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    paths = es.ensure_env_root_and_settings()
    assert paths["settings_file"].exists()
    config = es.load_settings(paths["settings_file"])
    assert isinstance(config, dict)


def test_update_settings_nested(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    paths = es.ensure_env_root_and_settings()
    es.update_settings(paths["settings_file"], {"duckdb": {"custom": 42}})
    cfg = es.load_settings(paths["settings_file"])
    env_type, env_name, project_name = es.detect_runtime_context()
    duckdb_config = cfg[env_type][env_name][project_name]["duckdb"]
    assert duckdb_config["custom"] == 42


def test_update_settings_overwrite_non_dict(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    paths = es.ensure_env_root_and_settings()

    # Overwrite the entire `duckdb` section
    es.update_settings(paths["settings_file"], {"duckdb": "just a string"})
    cfg = es.load_settings(paths["settings_file"])

    env_type, env_name, project_name = es.detect_runtime_context()
    assert cfg[env_type][env_name][project_name]["duckdb"] == "just a string"


def test_create_runtime_dirs_memory(tmp_path):
    config = {
        "duckdb": {
            "duckdb_mode": "memory",
            "memory_temp_directory": str(tmp_path / "temp_dir"),
            "persistent_db_file_path": str(tmp_path / "db" / "edamorph.db"),
        }
    }
    paths = {
        "logs": tmp_path / "logs",
        "cache": tmp_path / "cache",
        "temp": tmp_path / "temp_dir",
        "database": tmp_path / "db",
        "db_file": tmp_path / "db" / "edamorph.db",
    }
    es.create_runtime_dirs(config, paths)
    assert paths["logs"].exists()
    assert paths["cache"].exists()
    assert paths["temp"].exists()


def test_create_runtime_dirs_persistent(tmp_path):
    db_path = tmp_path / "db" / "edamorph.db"
    config = {
        "duckdb": {
            "duckdb_mode": "persistent",
            "memory_temp_directory": str(tmp_path / "temp"),
            "persistent_db_file_path": str(db_path),
        }
    }
    paths = {
        "logs": tmp_path / "logs",
        "cache": tmp_path / "cache",
        "temp": tmp_path / "temp",
        "database": tmp_path / "db",
        "db_file": db_path,
    }
    es.create_runtime_dirs(config, paths)
    assert db_path.parent.exists()
    assert paths["logs"].exists()
    assert paths["cache"].exists()


def test_load_settings_reads_correct(tmp_path):
    file = tmp_path / "settings.json"
    data = {"a": 1}
    with open(file, "w") as f:
        json.dump(data, f)
    result = es.load_settings(file)
    assert result == data