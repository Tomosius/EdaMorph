# edamorph/core/input_output/utils.py
"""
Universal DataFrame → Arrow Export Utilities for EdaMorph
---------------------------------------------------------
Handles conversion and streaming of supported DataFrame-like objects
(Polars, Pandas, PyArrow, Vaex, DuckDB, etc) to Arrow IPC,
with optional columns and row slicing.

Structure:
    - detect_dataframe_backend
    - to_arrow_table (dispatch)
    - individual converters (per backend)
    - arrow_preview_stream (main entrypoint for FastAPI/JS)
"""

import io
from typing import Optional, Sequence, Tuple, Any
from fastapi.responses import StreamingResponse

def detect_dataframe_backend(df: Any) -> Optional[str]:
    """
    Detects which dataframe library a given object belongs to.
    Returns backend name as string, or None if not recognized.

    Parameters
    ----------
    df : object
        DataFrame-like object to check.

    Returns
    -------
    backend : str or None
        "polars", "pandas", "pyarrow", "vaex", "duckdb", or None.
    """
    mod = type(df).__module__
    name = type(df).__name__
    if mod.startswith("polars."):
        return "polars"
    if mod.startswith("pandas."):
        return "pandas"
    if mod.startswith("pyarrow."):
        return "pyarrow"
    if mod.startswith("vaex."):
        return "vaex"
    if mod.startswith("duckdb."):
        return "duckdb"
    if name == "DuckDBPyRelation":
        return "duckdb"
    return None

# ------- Individual backend converters -------

def polars_to_arrow(df, columns=None, row_range=None):
    """
    Converts Polars DataFrame or LazyFrame to PyArrow Table.
    """
    import polars as pl
    if isinstance(df, pl.LazyFrame):
        df = df.collect()
    # 🔑 Clone to avoid "already mutably borrowed" errors
    df = df.clone()
    if columns:
        df = df.select(columns)
    if row_range:
        df = df.slice(row_range[0], row_range[1] - row_range[0])
    return df.to_arrow()

def pandas_to_arrow(df, columns=None, row_range=None):
    """
    Converts Pandas DataFrame to PyArrow Table.
    """
    import pandas as pd
    import pyarrow as pa
    df2 = df.copy()
    if columns:
        df2 = df2[columns]
    if row_range:
        df2 = df2.iloc[row_range[0]:row_range[1]]
    return df2.__arrow_table__()

def pyarrow_table_to_arrow(df, columns=None, row_range=None):
    """
    Returns a filtered PyArrow Table.
    """
    import pyarrow as pa
    t = df
    if columns:
        t = t.select(columns)
    if row_range:
        t = t.slice(row_range[0], row_range[1] - row_range[0])
    return t

def vaex_to_arrow(df, columns=None, row_range=None):
    """
    Converts Vaex DataFrame to PyArrow Table.
    """
    table = df.to_arrow_table()
    if columns:
        table = table.select(columns)
    if row_range:
        table = table.slice(row_range[0], row_range[1] - row_range[0])
    return table

def duckdb_to_arrow(df, columns=None, row_range=None):
    """
    Converts DuckDB relation to PyArrow Table.
    """
    import duckdb
    if columns or row_range:
        query = "SELECT "
        query += ", ".join(columns) if columns else "*"
        query += " FROM df"
        if row_range:
            limit = row_range[1] - row_range[0]
            offset = row_range[0]
            query += f" LIMIT {limit} OFFSET {offset}"
        con = duckdb.connect()
        con.register('df', df)
        result = con.execute(query).arrow()
        return result
    else:
        return df.arrow()

# ------- Universal dispatcher -------

def to_arrow_table(df, columns=None, row_range=None):
    """
    Converts any supported dataframe to a PyArrow Table.
    """
    backend = detect_dataframe_backend(df)
    if backend == "polars":
        return polars_to_arrow(df, columns, row_range)
    elif backend == "pandas":
        return pandas_to_arrow(df, columns, row_range)
    elif backend == "pyarrow":
        return pyarrow_table_to_arrow(df, columns, row_range)
    elif backend == "vaex":
        return vaex_to_arrow(df, columns, row_range)
    elif backend == "duckdb":
        return duckdb_to_arrow(df, columns, row_range)
    else:
        raise ValueError(f"Unsupported DataFrame type: {type(df)}")

# ------- Streaming for FastAPI -------

def arrow_preview_stream(
    df: Any,
    columns: Optional[Sequence[str]] = None,
    row_range: Optional[Tuple[int, int]] = None,
    n_rows: Optional[int] = 100,
) -> StreamingResponse:
    """
    Given any supported DataFrame, returns a StreamingResponse containing
    an Arrow IPC stream with the specified rows/columns.

    If row_range is not set, n_rows applies as [0:n_rows].

    Parameters
    ----------
    df : DataFrame-like object
        The data to export (Polars, Pandas, Arrow Table, Vaex, DuckDB, etc).
    columns : list/tuple of str, optional
        Columns to include. If None, use all columns.
    row_range : tuple (start, stop), optional
        Row range to include (0-based, [start:stop)). If None, uses n_rows.
    n_rows : int, optional
        Number of rows (default 100) if row_range is not set.

    Returns
    -------
    StreamingResponse
    """
    if df is None:
        return StreamingResponse(io.BytesIO(), media_type="application/vnd.apache.arrow.stream")
    if row_range is None and n_rows is not None:
        row_range = (0, n_rows)
    try:
        arrow_tbl = to_arrow_table(df, columns, row_range)
        import pyarrow as pa
        buf = io.BytesIO()
        with pa.ipc.new_stream(buf, arrow_tbl.schema) as writer:
            writer.write_table(arrow_tbl)
        buf.seek(0)
        return StreamingResponse(buf, media_type="application/vnd.apache.arrow.stream")
    except Exception as e:
        import logging
        logging.exception("Failed to export Arrow preview")
        return StreamingResponse(io.BytesIO(), media_type="application/vnd.apache.arrow.stream")