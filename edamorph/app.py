"""App initialization for EdaMorph using Polars only."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import polars as pl

from edamorph.settings import settings, logger
from edamorph.routes import router as core_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Exploratory Data Analysis API",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.mount(
    settings.STATIC_URL,
    StaticFiles(directory=settings.STATIC_DIR),
    name="static"
)

app.include_router(core_router)
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

@app.on_event("startup")
async def startup_event():
    """
    (Optional) Load a default DataFrame into app.state, or initialize resources.
    """
    # Example: app.state.df = pl.read_csv("data.csv")  # optional!
    logger.info("🚀 EdaMorph startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    (Optional) Clean up resources.
    """
    logger.info("🛑 EdaMorph shutdown complete.")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "debug": settings.DEBUG
        }
    )