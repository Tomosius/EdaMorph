"""
📁 edamorph.routes

🔧 Centralized route registration for the EdaMorph FastAPI app.

This module aggregates all feature-specific routers discovered dynamically
from the `edamorph.backend` package (e.g., settings, import, transformation).
Each submodule inside `backend/` must expose a `router` object.

✅ Purpose:
- Dynamically include all modular routers from submodules.
- Avoid repetitive manual `include_router()` calls.
- Serve as the single place where all backend logic is registered to the app.

🎯 Example usage in `app.py`:
    from edamorph.routes import router
    app.include_router(router)
"""

from fastapi import APIRouter
from edamorph.core import routers  # ✅ Auto-discovered routers from submodules

# ✅ Create a global APIRouter instance for app-wide use
router = APIRouter()

# 🔌 Register each discovered router from backend submodules
for r in routers:
    router.include_router(r)

"""
💡 Notes:
- Each backend submodule (e.g., `app_settings`, `data_import`) should define a `router` in its `__init__.py`.
- This allows for seamless plug-and-play extensibility of new app components.
- Keeps the main app routing clean and modular.
"""