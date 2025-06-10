# edamorph/backend/app_settings/routes.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from .views import render_settings  # ✅ Import view

router = APIRouter()

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return render_settings(request)