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
"""

from pathlib import Path
import json
from platformdirs import PlatformDirs
from typing import Any, Dict


APP_NAME = "edamorph"
APP_AUTHOR = "Tomas Pecukevicius"


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
    Ensure the root directory and default settings.json file exist.
    """
    paths = get_env_paths()
    paths["root"].mkdir(parents=True, exist_ok=True)

    if not paths["settings_file"].exists():
        default_config = {
            "duckdb": {
                "edamorph_settings_file": True,
                "duckdb_mode": "memory",
                "memory_ram_limit_mb": 2048,
                "memory_temp_directory": str(paths["temp"]),
                "persistent_db_file_path": str(paths["db_file"])
            }
        }
        with open(paths["settings_file"], "w") as f:
            json.dump(default_config, f, indent=4)

    return paths


def load_settings(settings_file: Path) -> Dict[str, Any]:
    """
    Load settings.json into a dictionary.
    """
    with open(settings_file, "r") as f:
        return json.load(f)


def update_settings(settings_file: Path, updates: Dict[str, Any]) -> None:
    """
    Update settings.json with provided nested keys (only 1 level deep).
    Overwrites only keys provided in updates.
    """
    settings = load_settings(settings_file)

    for key, value in updates.items():
        # If the section exists and both are dicts, update it
        if key in settings and isinstance(settings[key], dict) and isinstance(value, dict):
            settings[key].update(value)
        else:
            # Overwrite entire key
            settings[key] = value

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