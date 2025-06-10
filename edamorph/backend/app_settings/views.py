# edamorph/backend/app_settings/views.py

from fastapi import Request
from fastapi.templating import Jinja2Templates
from edamorph.settings import settings

templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

def render_settings(request: Request):
    """
    ✅ Handles rendering of the app_settings page.
    - Passes dynamic app configuration to the template.
    """
    return templates.TemplateResponse("app_settings/settings_main.html", {
        "request": request,
        "title": "Settings",
        "app_settings": settings,
    })