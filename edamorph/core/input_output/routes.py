"""
API Routes: Data Import (Polars)
-------------------------------
Handles CSV/file upload POSTs and info queries for frontend JS/HTMX.
Respects session_state settings for eager/lazy loading.
"""

import polars as pl
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
from edamorph.session import session_state

router = APIRouter(tags=["data-import"])

@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    lazy: bool = None  # <-- Can be provided or omitted
):
    """
    Accepts a file upload and loads into Polars (eager/lazy), following session state.
    - If `lazy` is passed in POST, that value overrides session default.
    - If not, uses session_state.polars_mode ("eager"/"lazy").
    Updates global session_state only.
    """
    # Decide on mode
    if lazy is None:
        mode = session_state.polars_mode
    else:
        mode = "lazy" if lazy else "eager"
        session_state.polars_mode = mode  # <-- update session for consistency

    try:
        if mode == "lazy":
            df = pl.scan_csv(file.file)
            session_state.lazy = True
        else:
            df = pl.read_csv(file.file)
            session_state.lazy = False

        session_state.set_df(
            df,
            name=file.filename,
            path=getattr(file, "filename", None),
            lazy=session_state.lazy
        )
        return {
            "success": True,
            "name": file.filename,
            "shape": df.schema if session_state.lazy else df.shape,
            "lazy": session_state.lazy
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {e}")

@router.get("/current_dataset")
def get_current_dataset_info():
    if getattr(session_state, "df", None) is None:
        return {"loaded": False}
    return {
        "loaded": True,
        "name": getattr(session_state, "df_name", None),
        "lazy": getattr(session_state, "lazy", False),
        "info": (
            session_state.df.schema if session_state.lazy
            else session_state.df.shape
        ),
        "polars_mode": session_state.polars_mode
    }