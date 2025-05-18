from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from edamorph.settings import settings  # ✅ Import your config

app = FastAPI()

# ✅ Use the paths from settings
app.mount(
    settings.STATIC_URL,
    StaticFiles(directory=settings.STATIC_DIR),
    name="static"
)

templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})