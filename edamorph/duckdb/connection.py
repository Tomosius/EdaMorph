import os
import duckdb
import logging
from edamorph.settings import settings

# ✅ Configure logging instead of print statements
logging.basicConfig(level=logging.DEBUG)  # ✅ Set to DEBUG for detailed logs
logger = logging.getLogger(__name__)


class DuckDBConnection:
    _instance = None  # ✅ Singleton instance
    _conn = None  # ✅ Stores the active connection

    def __new__(cls, db_path=None, existing_conn=None):
        """
        ✅ Creates a single DuckDB connection.
        - Uses `existing_conn` if provided.
        - Uses `DATABASE_URL` from settings by default.
        - Ensures metadata is initialized when needed.
        """

        if cls._instance is None:
            cls._instance = super().__new__(cls)

            # ✅ Use DATABASE_URL from settings if no path is provided
            db_path = db_path or settings.DATABASE_URL

            # ✅ Convert to absolute path if not using in-memory DB
            if db_path != ":memory:":
                db_path = os.path.abspath(db_path)

            logger.info(f"🔍 Connecting to DuckDB at: {db_path}")  # ✅ Debugging Step

            # ✅ Use the provided existing connection if available
            if existing_conn:
                cls._instance.conn = existing_conn
            else:
                cls._instance.conn = duckdb.connect(db_path, read_only=False)

            # ✅ Enable temp storage for in-memory DuckDB if needed
            if db_path == ":memory:" and settings.DUCKDB_TEMP_DIR:
                temp_dir = os.path.abspath(settings.DUCKDB_TEMP_DIR)
                os.makedirs(os.path.dirname(temp_dir), exist_ok=True)
                cls._instance.conn.execute(f"PRAGMA temp_directory='{temp_dir}';")
                logger.info(f"✅ DuckDB temp storage set to: {temp_dir}")



            logger.info(f"✅ Connected to DuckDB ({db_path})")

        return cls._instance



    def get_connection(self):
        """ ✅ Returns the active DuckDB connection. """
        return self.conn

    def close(self):
        """ ✅ Closes the DuckDB connection. """
        if self.conn:
            self.conn.close()
            logger.info("🛑 DuckDB session closed.")


# ✅ Default connection (uses DATABASE_URL from settings)
duckdb_connection = DuckDBConnection().get_connection()