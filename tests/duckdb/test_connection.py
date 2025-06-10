"""
🧪 tests/duckdb/test_connection.py

Test suite for `DuckDBConnection` singleton class in `edamorph.duckdb.connection`.

Covers:
- Singleton behavior
- Default and custom connection paths
- Temporary directory setup
- Manual close
- Reuse of existing connection
"""

import os
import duckdb
import tempfile
import pytest
from edamorph.duckdb.connection import DuckDBConnection


@pytest.fixture(autouse=True)
def reset_singleton():
    """
    Fixture to reset the singleton before each test.
    Prevents shared state between tests.
    """
    DuckDBConnection._instance = None
    yield
    DuckDBConnection._instance = None


def test_duckdb_singleton_behavior():
    """Ensure DuckDBConnection returns the same instance."""
    conn1 = DuckDBConnection()
    conn2 = DuckDBConnection()
    assert conn1 is conn2, "DuckDBConnection did not return a singleton instance"


def test_connection_returns_duckdb_connection_object():
    """Ensure get_connection() returns a duckdb.DuckDBPyConnection."""
    instance = DuckDBConnection()
    conn = instance.get_connection()
    assert isinstance(conn, duckdb.DuckDBPyConnection)


def test_custom_path_creates_db_file(tmp_path):
    """Ensure custom file path creates a DuckDB file on disk."""
    db_path = tmp_path / "test_duckdb.db"
    instance = DuckDBConnection(db_path=str(db_path))
    assert db_path.exists(), "Database file was not created"


def test_in_memory_connection_with_temp_directory(monkeypatch, tmp_path):
    """
    ✅ Test DuckDB in-memory with a custom temporary directory.
    🛠️ Patches environment variables used by settings (instead of modifying settings object directly).
    """
    monkeypatch.setenv("DATABASE_URL", ":memory:")
    monkeypatch.setenv("DUCKDB_TEMP_DIR", str(tmp_path / "temp"))

    # 🔄 Re-import the class after monkeypatching env (to ensure it uses new env values)
    from importlib import reload
    from edamorph import settings as settings_module
    reload(settings_module)  # Re-evaluate BaseSettings

    from edamorph.duckdb.connection import DuckDBConnection  # re-import with patched settings

    instance = DuckDBConnection()
    conn = instance.get_connection()

    # ✅ Connection works
    conn.execute("SELECT 42")


def test_connection_close():
    """Ensure connection closes properly."""
    instance = DuckDBConnection()
    conn = instance.get_connection()
    instance.close()

    with pytest.raises(Exception):
        conn.execute("SELECT 1")  # Should raise error after close


def test_existing_connection_reuse():
    """Ensure provided existing connection is used."""
    existing = duckdb.connect(":memory:")
    instance = DuckDBConnection(existing_conn=existing)
    assert instance.get_connection() is existing, "Existing connection not reused"