# edamorph/settings.py

import os
import json
import logging
from typing import List, Dict, Any
import msgspec
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Logger configuration
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("edamorph")

# ✅ Core paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_DIR = os.path.join(BASE_DIR, "app_settings")
DEFAULT_SETTINGS_PATH = os.path.join(SETTINGS_DIR, "default_settings.json")
USER_SETTINGS_PATH = os.path.join(SETTINGS_DIR, "user_settings.json")

# ✅ Default DuckDB settings (fallback values)
DEFAULT_SETTINGS = {
    "duckdb": {
        "use_in_memory": True,
        "db_file_path": os.path.join(BASE_DIR, "db", "edamorph.db"),
        "temp_directory": os.path.join(BASE_DIR, "db", "temp")
    }
}

# ✅ Ensure settings directory exists
os.makedirs(SETTINGS_DIR, exist_ok=True)

# ✅ Create default settings file if missing
if not os.path.exists(DEFAULT_SETTINGS_PATH):
    with open(DEFAULT_SETTINGS_PATH, "w") as f:
        json.dump(DEFAULT_SETTINGS, f, indent=4)
        logger.info("✅ Default settings file created.")

def load_json_settings() -> Dict[str, Any]:
    """Load and merge default and user settings."""
    settings = DEFAULT_SETTINGS.copy()

    # Load defaults explicitly from file (in case changed)
    if os.path.exists(DEFAULT_SETTINGS_PATH):
        with open(DEFAULT_SETTINGS_PATH, "r") as f:
            settings = json.load(f)

    # Override with user settings if present
    if os.path.exists(USER_SETTINGS_PATH):
        with open(USER_SETTINGS_PATH, "r") as f:
            user_settings = json.load(f)
            settings.update(user_settings)
            logger.info("✅ Loaded user settings.")
    else:
        logger.info("🔄 Using default settings (no user settings found).")

    return settings

# ✅ Load active JSON settings
json_settings = load_json_settings()

# ✅ Frozen app settings structure
class Settings(msgspec.Struct, frozen=True):
    APP_NAME: str = os.getenv("APP_NAME", "EdaMorph")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8000))

    BASE_DIR: str = BASE_DIR
    EXECUTION_PATH: str = os.getcwd()

    STATIC_URL: str = "/static"
    STATIC_DIR: str = os.path.join(BASE_DIR, "frontend/assets")
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "frontend/templates")

    # ✅ DuckDB settings (based on user or default config)
    DUCKDB_USE_MEMORY: bool = json_settings["duckdb"]["use_in_memory"]
    DATABASE_URL: str = ":memory:" if DUCKDB_USE_MEMORY else json_settings["duckdb"]["db_file_path"]
    DUCKDB_TEMP_DIR: str = json_settings["duckdb"]["temp_directory"]
    DB_DIR: str = os.path.dirname(json_settings["duckdb"]["db_file_path"])

    # ✅ CORS and security settings
    ALLOW_CREDENTIALS: bool = True
    ALLOW_ORIGINS: List[str] = msgspec.field(default_factory=lambda: ["*"])
    ALLOW_METHODS: List[str] = msgspec.field(default_factory=lambda: ["*"])
    ALLOW_HEADERS: List[str] = msgspec.field(default_factory=lambda: ["*"])

# ✅ Instantiate immutable settings object
settings = Settings()

# ✅ Ensure database directories exist
os.makedirs(settings.DB_DIR, exist_ok=True)
os.makedirs(settings.DUCKDB_TEMP_DIR, exist_ok=True)