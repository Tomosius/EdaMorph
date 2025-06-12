"""
EdaMorph Environment Setup Utility
----------------------------------
Handles automatic setup of persistent environment folders and configuration
for the EdaMorph application using platform-appropriate locations.

This module ensures:
- A root folder (e.g., ~/.config/edamorph/) is created.
- settings.json is initialized and updated as needed.
- Runtime folders (temp, cache, database, logs) are created only when needed.
- Utility methods allow reading, writing, and merging settings.
- Settings are stored per environment and project for full flexibility.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple
from platformdirs import PlatformDirs

APP_NAME = "edamorph"
APP_AUTHOR = "Tomas Pecukevicius"

def sanitize_name(name: str) -> str:
    """Sanitize name for use in JSON keys (remove slashes, normalize)."""
    return name.replace(" ", "_").replace("/", "_").lower()

def detect_env_type() -> str:
    """Detect environment type (conda, mamba, venv, pyenv, global, etc)."""
    if "CONDA_PREFIX" in os.environ:
        exe = os.environ.get("CONDA_EXE", "conda").lower()
        if "mamba" in exe:
            return "mamba"
        elif "miniconda" in exe:
            return "miniconda"
        elif "anaconda" in exe:
            return "anaconda"
        else:
            return "conda"
    if "PYENV_VERSION" in os.environ:
        return "pyenv"
    if "POETRY_ACTIVE" in os.environ:
        return "poetry"
    if hasattr(sys, "real_prefix") or (hasattr(sys, 'base_prefix') and sys.prefix != sys.base_prefix):
        return "venv"
    return "global"

def detect_env_name() -> str:
    """Detect the name of the current environment."""
    if "CONDA_PREFIX" in os.environ:
        return os.environ.get("CONDA_DEFAULT_ENV", Path(os.environ["CONDA_PREFIX"]).name)
    if "PYENV_VERSION" in os.environ:
        return os.environ["PYENV_VERSION"]
    return Path(sys.prefix).name

def detect_project_name() -> str:
    """Detect the current project name or fallback."""
    return Path.cwd().name or detect_env_name() or detect_env_type()

def detect_runtime_context() -> Tuple[str, str, str]:
    """
    Detect full context as a tuple: (env_type, env_name, project_name)
    """
    return (
        sanitize_name(detect_env_type()),
        sanitize_name(detect_env_name()),
        sanitize_name(detect_project_name()),
    )

def get_env_paths() -> Dict[str, Path]:
    """
    Return standard EdaMorph platform-specific directories.
    """
    dirs = PlatformDirs(appname=APP_NAME, appauthor=APP_AUTHOR)
    root = Path(dirs.user_data_dir)
    return {
        "root": root,
        "settings_file": root / "settings.json",
        "logs": root / "logs",
        "cache": root / "cache",
        "temp": root / "temp",
        "database": root / "database",
        "db_file": root / "database" / "edamorph.db",
    }

def ensure_env_root_and_settings() -> Dict[str, Path]:
    """
    Ensure the root directory and default settings.json file exist,
    and environment/project specific settings branch is created.
    """
    paths = get_env_paths()
    paths["root"].mkdir(parents=True, exist_ok=True)

    if not paths["settings_file"].exists():
        with open(paths["settings_file"], "w") as f:
            json.dump({}, f, indent=4)

    env_type, env_name, project_name = detect_runtime_context()
    full_settings = load_settings(paths["settings_file"])

    if env_type not in full_settings:
        full_settings[env_type] = {}
    if env_name not in full_settings[env_type]:
        full_settings[env_type][env_name] = {}
    if project_name not in full_settings[env_type][env_name]:
        full_settings[env_type][env_name][project_name] = {
            "duckdb": {
                "edamorph_settings_file": True,
                "duckdb_mode": "memory",
                "memory_ram_limit_mb": 2048,
                "memory_temp_directory": str(paths["temp"]),
                "persistent_db_file_path": str(paths["db_file"])
            }
        }
        with open(paths["settings_file"], "w") as f:
            json.dump(full_settings, f, indent=4)

    return paths

def load_settings(settings_file: Path) -> Dict[str, Any]:
    """
    Load settings.json into a dictionary.
    """
    with open(settings_file, "r") as f:
        return json.load(f)

def update_settings(settings_file: Path, updates: Dict[str, Any]) -> None:
    """
    Update settings.json with provided nested keys in the current env/project scope.
    """
    settings = load_settings(settings_file)
    env_type, env_name, project_name = detect_runtime_context()

    project_settings = settings.setdefault(env_type, {}).setdefault(env_name, {}).setdefault(project_name, {})

    for key, value in updates.items():
        if key in project_settings and isinstance(project_settings[key], dict) and isinstance(value, dict):
            project_settings[key].update(value)
        else:
            project_settings[key] = value

    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)

def create_runtime_dirs(config: Dict[str, Any], paths: Dict[str, Path]) -> None:
    """
    Conditionally create folders required at runtime based on current settings.
    """
    duckdb_conf = config.get("duckdb", {})
    mode = duckdb_conf.get("duckdb_mode")

    if mode == "memory":
        Path(duckdb_conf["memory_temp_directory"]).mkdir(parents=True, exist_ok=True)
    elif mode == "persistent":
        Path(duckdb_conf["persistent_db_file_path"]).parent.mkdir(parents=True, exist_ok=True)

    paths["logs"].mkdir(exist_ok=True)
    paths["cache"].mkdir(exist_ok=True)