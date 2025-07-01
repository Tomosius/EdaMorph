"""
API Routes: Data Import (Universal)
-----------------------------------
Handles CSV/file upload POSTs and info queries for frontend JS/HTMX.
Supports Polars, Pandas, Arrow, and more in the future.
"""

# Polars is always optional, can add Pandas etc.
import polars as pl
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(tags=["data-import"])


@router.post("/import")
async def import_data(
        file: UploadFile = File(...),
        lazy: bool = False
):
    """
    Accepts a file upload and loads it into a DataFrame.
    Updates global session_state, supporting Polars or others.
    """
    try:
        # Use file extension to choose backend (for now)
        ext = file.filename.split(".")[-1].lower()
        name = file.filename
        file_path = name

        if ext in {"csv", "tsv"}:
            # Use Polars for CSV, can expand to Pandas if you want
            if lazy:
                df = pl.scan_csv(file.file)
            else:
                # Workaround: file.file is a SpooledTemporaryFile, needs to be reset for each backend
                file.file.seek(0)
                df = pl.read_csv(file.file)
            backend = "polars"
        elif ext in {"parquet"}:
            file.file.seek(0)
            df = pl.read_parquet(file.file)
            backend = "polars"
        elif ext in {"arrow", "feather"}:
            file.file.seek(0)
            df = pl.read_ipc(file.file)
            backend = "polars"
        # TODO: add Pandas, Vaex, etc as needed here
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

        # Store in session, can be universal!
        session_state.set_df(
            df,
            name=name,
            path=file_path,
            lazy=lazy,
        )
        return {
            "success": True,
            "name": name,
            "path": file_path,
            "shape": df.schema if lazy else getattr(df, "shape", None),
            "lazy": lazy,
            "backend": backend
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {e}")


@router.get("/current_dataset")
def get_current_dataset_info():
    df = getattr(session_state, "df", None)
    if df is None:
        return {"loaded": False}
    # Universal backend detection (polars, pandas, pyarrow, etc)
    from edamorph.core.input_output.utils import detect_dataframe_backend
    backend = detect_dataframe_backend(df)
    # Get info universal way
    info = None
    colnames = None
    shape = None
    try:
        # Try Arrow table extraction for columns and shape
        from edamorph.core.input_output.utils import to_arrow_table
        arrow_tbl = to_arrow_table(df)
        colnames = [field.name for field in arrow_tbl.schema]
        shape = (arrow_tbl.num_rows, arrow_tbl.num_columns)
        info = shape
    except Exception:
        # Fallbacks for Pandas/Polars
        if hasattr(df, "shape"):
            shape = df.shape
        if hasattr(df, "columns"):
            colnames = list(df.columns)
        info = shape

    return {
        "loaded": True,
        "name": getattr(session_state, "df_name", None),
        "backend": backend,
        "shape": shape,
        "columns": colnames,
        "info": info,
    }


from fastapi.responses import StreamingResponse
from edamorph.session import session_state
from edamorph.core.input_output.utils import arrow_preview_stream


@router.get("/arrow_preview")
def arrow_preview():
    """
    Streams first N rows of the current DataFrame as Arrow IPC for JS preview.
    """
    df = getattr(session_state, "df", None)
    if df is None:
        # Return empty IPC stream
        import io
        return StreamingResponse(io.BytesIO(), media_type="application/vnd.apache.arrow.stream")
    return arrow_preview_stream(df, n_rows=10)  # Or any number you want!
