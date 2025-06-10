# tests/test_settings.py

import os
import json
from edamorph.settings import (
    SETTINGS_DIR,
    DEFAULT_SETTINGS_PATH,
    USER_SETTINGS_PATH,
    json_settings,
    settings,
)


def test_default_settings_file_exists():
    """Ensure the default_settings.json file exists."""
    assert os.path.exists(DEFAULT_SETTINGS_PATH), "Default settings file is missing."


def test_default_settings_has_required_keys():
    """Ensure duckdb config has all required fields."""
    assert "duckdb" in json_settings, "Missing 'duckdb' section in settings."

    duckdb_settings = json_settings["duckdb"]
    required_keys = {"use_in_memory", "db_file_path", "temp_directory"}

    missing_keys = required_keys - duckdb_settings.keys()
    assert not missing_keys, f"Missing keys in duckdb settings: {missing_keys}"


def test_user_settings_override_if_exists(monkeypatch, tmp_path):
    """Check if user settings override defaults when present."""
    # Setup temp settings files
    test_dir = tmp_path / "app_settings"
    test_dir.mkdir()

    default_path = test_dir / "default_settings.json"
    user_path = test_dir / "user_settings.json"

    default_data = {
        "duckdb": {
            "use_in_memory": True,
            "db_file_path": "should_be_overridden.db",
            "temp_directory": "temp_default"
        }
    }

    user_data = {
        "duckdb": {
            "use_in_memory": False,
            "db_file_path": "custom.db",
            "temp_directory": "temp_custom"
        }
    }

    default_path.write_text(json.dumps(default_data, indent=4))
    user_path.write_text(json.dumps(user_data, indent=4))

    # Patch paths in module
    monkeypatch.setattr("edamorph.settings.DEFAULT_SETTINGS_PATH", str(default_path))
    monkeypatch.setattr("edamorph.settings.USER_SETTINGS_PATH", str(user_path))
    from edamorph.settings import load_json_settings

    combined = load_json_settings()
    assert combined["duckdb"]["use_in_memory"] is False
    assert combined["duckdb"]["db_file_path"] == "custom.db"
    assert combined["duckdb"]["temp_directory"] == "temp_custom"


def test_settings_instance_has_expected_fields():
    """Verify key settings paths and values are valid."""
    assert settings.DATABASE_URL, "DATABASE_URL should not be empty"
    assert settings.DUCKDB_TEMP_DIR, "DUCKDB_TEMP_DIR should not be empty"

    assert os.path.isdir(settings.DB_DIR), f"{settings.DB_DIR} does not exist"
    assert os.path.isdir(settings.DUCKDB_TEMP_DIR), f"{settings.DUCKDB_TEMP_DIR} does not exist"

    assert settings.STATIC_DIR.endswith("frontend/assets")
    assert settings.TEMPLATES_DIR.endswith("frontend/templates")