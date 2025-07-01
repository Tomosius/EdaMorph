"""
Index Page Views for EdaMorph
-----------------------------
Renders the main index.html, showing dataset info if loaded.
Front-end JS will request Arrow preview for table rendering.
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from edamorph.session import session_state
from edamorph.settings import settings

router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

@router.get("/")
async def index(request: Request):
    """
    Renders the index page with dataset summary if loaded.
    Data table is rendered in the browser from Arrow IPC via JavaScript.
    """
    dataset_loaded = session_state.df is not None
    df = session_state.df

    # Build a minimal context (for Jinja, not the data preview itself)
    context = {
        "request": request,
        "dataset_loaded": dataset_loaded,
        "dataset_name": session_state.df_name,
        "dataset_shape": None,
        "column_names": None,
        # No dataset_preview, JS will handle via /arrow_preview endpoint
    }

    # Populate shape & columns for header/info if available
    if dataset_loaded:
        try:
            # Use Arrow conversion for column names and shape (universal for all DF types)
            from edamorph.core.input_output.utils import to_arrow_table
            arrow_tbl = to_arrow_table(df)
            context["dataset_shape"] = (arrow_tbl.num_rows, arrow_tbl.num_columns)
            context["column_names"] = [field.name for field in arrow_tbl.schema]
        except Exception:
            # Fallback for older/unknown types
            if hasattr(df, "columns"):
                context["column_names"] = list(df.columns)
            if hasattr(df, "shape"):
                context["dataset_shape"] = df.shape

    return templates.TemplateResponse("index.html", context)