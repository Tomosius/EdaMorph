"""
Data Import Views for EdaMorph
------------------------------
Handles CSV and supported file uploads and loads them into Polars,
and stores result in session_state.
"""

import polars as pl
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse

from edamorph.session import session_state  # <-- Use this!

router = APIRouter()

@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    lazy: bool = False
):
    """
    Upload a file and load it into Polars, then update session_state.
    """
    try:
        if lazy:
            df = pl.scan_csv(file.file)
        else:
            df = pl.read_csv(file.file)
        # Update session_state (central place)
        session_state.set_df(
            df,
            name=file.filename,
            path=getattr(file, "filename", None),
            lazy=lazy,
        )
        return JSONResponse({
            "success": True,
            "name": file.filename,
            "shape": df.schema if lazy else df.shape,
            "lazy": lazy
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {e}")

@router.get("/current_dataset")
def get_current_dataset_info():
    if session_state.df is None:
        return {"loaded": False}
    return {
        "loaded": True,
        "name": session_state.df_name,
        "lazy": session_state.lazy,
        "info": (
            session_state.df.schema if session_state.lazy
            else session_state.df.shape
        )
    }