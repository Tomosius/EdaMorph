"""App initialization for EdaMorph."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from edamorph.settings import settings, logger
from edamorph.routes import router as core_router
from edamorph.duckdb.connection import DuckDBConnection

# ✅ Create FastAPI instance
app = FastAPI(
    title=settings.APP_NAME,
    description="Exploratory Data Analysis API",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ✅ Mount static files
app.mount(
    settings.STATIC_URL,
    StaticFiles(directory=settings.STATIC_DIR),
    name="static"
)

# ✅ Include centralized router
app.include_router(core_router)

# ✅ Jinja2 templates setup
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

# ✅ Startup event for DuckDB initialization
@app.on_event("startup")
async def startup_event():
    app.state.db = DuckDBConnection().get_connection()
    logger.info("🚀 DuckDB connection initialized at startup.")

# ✅ Shutdown event for DuckDB connection closure
@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, 'db'):
        DuckDBConnection().close()
        logger.info("🛑 DuckDB connection closed at shutdown.")

# ✅ Root endpoint
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "debug": settings.DEBUG
        }
    )