"""
API Routes: Data Import (Universal)
-----------------------------------
Handles CSV/file upload POSTs and info queries for frontend JS/HTMX.
Supports Polars, Pandas, Arrow, and more in the future.
"""

import os
import tempfile

# Polars is always optional, can add Pandas etc.
import polars as pl
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from edamorph.core.input_output.utils import arrow_preview_stream
from edamorph.session import session_state

router = APIRouter(tags=["data-import"])


# ... imports ...

@router.post("/import")
async def import_data(
        file: UploadFile = File(...),
        lazy: bool = False,
):
    """
    Handles file uploads and loads data into a DataFrame.
    """
    try:
        ext = file.filename.split(".")[-1].lower()
        df_name = file.filename  # Canonical display name

        # For temp path, use only if lazy
        temp_path = None
        if ext in {"csv", "tsv"} and lazy:
            tempdir = tempfile.gettempdir()
            temp_path = os.path.join(tempdir, df_name)
            with open(temp_path, "wb") as out_file:
                file.file.seek(0)
                out_file.write(file.file.read())
            df = pl.scan_csv(temp_path)
        elif ext in {"csv", "tsv"}:
            file.file.seek(0)
            df = pl.read_csv(file.file)
        elif ext == "parquet":
            file.file.seek(0)
            df = pl.read_parquet(file.file)
        elif ext in {"arrow", "feather"}:
            file.file.seek(0)
            df = pl.read_ipc(file.file)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

        # Store in session, always using explicit names
        session_state.set_df(
            df,
            name=df_name,
            path=temp_path,  # Only not None if lazy
            lazy=lazy,
        )

        # Return fields matching session state
        return {
            "success": True,
            "df_name": df_name,
            "df_lazy": lazy,
            "shape": df.schema if lazy else getattr(df, "shape", None),
            "backend": "polars",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {e}")


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
    return arrow_preview_stream(df)  # Or any number you want!
