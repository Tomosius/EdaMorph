"""
EdaMorph Application Settings
-----------------------------
Loads and manages all core, environment, and path settings for EdaMorph.

- Uses `.env` for simple environment overrides (host, port, debug)
- Provides a structured `Settings` object using msgspec.Struct
- NO runtime reloading or user-edited config here—only static app config!
"""

import os
import logging
from typing import List
from dotenv import load_dotenv
from pathlib import Path
import msgspec

# === App meta/config ===
APP_NAME = "EdaMorph"
APP_AUTHOR = "Tomas Pecukevicius"

# === .env ===
load_dotenv()

# === Logging ===
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(APP_NAME)

# === Paths ===
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
EXECUTION_PATH = os.getcwd()

# --- Platform/user/project folders can still be set up if you want! ---
# If you want per-project cache or temp, keep this, else simplify further.
DATA_ROOT = os.path.join(APP_ROOT, "data")
TEMP_DIR = os.path.join(APP_ROOT, "tmp")
CACHE_DIR = os.path.join(APP_ROOT, "cache")
LOGS_DIR = os.path.join(APP_ROOT, "logs")

# --- Ensure folders exist at startup ---
for _dir in (DATA_ROOT, TEMP_DIR, CACHE_DIR, LOGS_DIR):
    os.makedirs(_dir, exist_ok=True)

# === Settings Struct ===
class Settings(msgspec.Struct, frozen=True):
    """
    Global, immutable settings for EdaMorph.
    No runtime/user-edited config here.
    """
    APP_NAME: str = APP_NAME
    VERSION: str = os.getenv("VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8000))
    APP_ROOT: str = APP_ROOT
    EXECUTION_PATH: str = EXECUTION_PATH
    DATA_ROOT: str = DATA_ROOT
    TEMP_DIR: str = TEMP_DIR
    CACHE_DIR: str = CACHE_DIR
    LOGS_DIR: str = LOGS_DIR
    STATIC_URL: str = "/static"
    STATIC_DIR: str = os.path.join(APP_ROOT, "frontend/assets")
    TEMPLATES_DIR: str = os.path.join(APP_ROOT, "frontend/templates")
    ALLOW_CREDENTIALS: bool = True
    ALLOW_ORIGINS: List[str] = msgspec.field(default_factory=lambda: ["*"])
    ALLOW_METHODS: List[str] = msgspec.field(default_factory=lambda: ["*"])
    ALLOW_HEADERS: List[str] = msgspec.field(default_factory=lambda: ["*"])

settings = Settings()