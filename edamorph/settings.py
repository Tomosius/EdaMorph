from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    """
    ✅ Manages app configuration, loading values from `.env` when available.
    - Defaults ensure the app runs even without `.env`.
    - Automatically type-converts values (e.g., `PORT` → int, `DEBUG` → bool).
    """

    # ✅ App Info (Overrides from `.env`)
    APP_NAME: str = "EdaMorph"
    VERSION: str = "1.0.0"
    DEBUG: bool = True  # Pydantic will auto-parse "true"/"false"

    # ✅ Server Config
    HOST: str = "127.0.0.1"
    PORT: int = 8000  # Pydantic auto-converts string to int

    # ✅ Base Paths
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))  # Project root
    EXECUTION_PATH: str = os.getcwd()

    # ✅ Static & Templates
    STATIC_URL: str = "/static"
    STATIC_DIR: str = os.path.join(BASE_DIR, "frontend/assets")
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "frontend/templates")

    # ✅ Database (Uses .env to allow overrides)
    DATABASE_URL: str = ":memory:"  # Default is in-memory

    def __init__(self, **kwargs):
        """
        ✅ Runs after settings are loaded from `.env`.
        - Ensures `DATABASE_URL` is an absolute path if not `:memory:`.
        """
        super().__init__(**kwargs)

        # ✅ Ensure DATABASE_URL is absolute if it's a file
        if self.DATABASE_URL != ":memory:":
            self.DATABASE_URL = os.path.abspath(
                os.path.join(os.path.dirname(__file__), self.DATABASE_URL)
            )

        print(f"🔍 DATABASE_URL resolved to: {self.DATABASE_URL}")

    # ✅ DuckDB Temp File
    CUSTOM_TEMP_PATH: str = ""
    DUCKDB_TEMP_DIR: str = ""

    def setup_duckdb_temp(self):
        """
        ✅ Determines the correct temp directory for DuckDB.
        - Uses `CUSTOM_TEMP_PATH` if defined.
        - Otherwise, defaults to a project-based temp file.
        """
        self.DUCKDB_TEMP_DIR = (
            self.CUSTOM_TEMP_PATH if self.CUSTOM_TEMP_PATH
            else os.path.join(self.EXECUTION_PATH, f"edamorph_tmp_{os.path.basename(self.EXECUTION_PATH)}.db")
        )

    # ✅ CORS Settings (Overridable via .env)
    ALLOW_ORIGINS: list[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list[str] = ["*"]
    ALLOW_HEADERS: list[str] = ["*"]

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        env_file_encoding = 'utf-8'


# ✅ Create global settings instance
settings = Settings()
settings.setup_duckdb_temp()

print("🔥 FINAL SETTINGS:", settings.dict())

