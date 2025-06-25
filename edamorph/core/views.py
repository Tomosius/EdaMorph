"""
Index Page Views for EdaMorph
-----------------------------
Renders the main index.html, showing dataset info if loaded.
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
    """
    dataset_loaded = session_state.df is not None
    context = {
        "request": request,
        "dataset_loaded": dataset_loaded,
        "dataset_name": session_state.df_name,
        "dataset_shape": None,
        "dataset_preview": None,
    }
    if dataset_loaded:
        # For eager: use head(). For lazy: need to collect().
        df = session_state.df
        if session_state.lazy:
            preview_df = df.head(5).collect().to_pandas()
            shape = df.schema
        else:
            preview_df = df.head(5).to_pandas()
            shape = df.shape
        context["dataset_shape"] = shape
        context["dataset_preview"] = preview_df.to_html(classes="table table-sm table-striped", index=False)

    return templates.TemplateResponse("index.html", context)