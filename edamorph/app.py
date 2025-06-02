"""App initialization for EdaMorph."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from edamorph.settings import settings  # ✅ App config

# ✅ Create the FastAPI app instance
app = FastAPI(title="EdaMorph", version="1.0.0")

# ✅ Static files mounting
app.mount(
    settings.STATIC_URL,
    StaticFiles(directory=settings.STATIC_DIR),
    name="static"
)

# ✅ Jinja2 templates config
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)


# ✅ Example route
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "debug": settings.DEBUG  # ✅ Pass DEBUG into Jinja context
        }
    )