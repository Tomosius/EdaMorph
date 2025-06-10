# edamorph/settings.py

import os
import logging
from typing import List
import msgspec
from dotenv import load_dotenv

load_dotenv()

# ✅ Logger configuration
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("edamorph")


class Settings(msgspec.Struct, frozen=True):
    APP_NAME: str = os.getenv("APP_NAME", "EdaMorph")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8000))

    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    EXECUTION_PATH: str = os.getcwd()

    STATIC_URL: str = "/static"
    STATIC_DIR: str = os.path.join(BASE_DIR, "frontend/assets")
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "frontend/templates")

    DB_DIR: str = os.path.join(BASE_DIR, "db")
    DATABASE_URL: str = os.getenv("DATABASE_URL", ":memory:")

    DUCKDB_TEMP_DIR: str = os.getenv(
        "DUCKDB_TEMP_DIR", os.path.join(DB_DIR, "temp")
    )

    ALLOW_CREDENTIALS: bool = True
    ALLOW_ORIGINS: List[str] = msgspec.field(default_factory=lambda: ["*"])
    ALLOW_METHODS: List[str] = msgspec.field(default_factory=lambda: ["*"])
    ALLOW_HEADERS: List[str] = msgspec.field(default_factory=lambda: ["*"])


settings = Settings()

# Ensure directories exist
os.makedirs(settings.DB_DIR, exist_ok=True)
os.makedirs(settings.DUCKDB_TEMP_DIR, exist_ok=True)