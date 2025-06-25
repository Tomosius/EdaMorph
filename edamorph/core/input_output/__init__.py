"""
📦 app_settings package

🧩 This package encapsulates all logic related to application settings,
including routing, rendering templates, and any future settings-related logic.

✅ Purpose:
- Isolate all settings-related features from the main app logic.
- Keep the structure modular, readable, and maintainable.
- Automatically expose the `router` for discovery by the global router system.

📂 Folder Structure:
    ├── app_settings/
    │   ├── __init__.py         ◀️ This file
    │   ├── routes.py           ▶️ Defines settings-related FastAPI routes
    │   ├── views.py            ▶️ Handles template rendering or UI logic

🎯 Usage:
- The `__all__` list makes `router` accessible when importing this package.
- Ensures `from edamorph.backend.app_settings import router` works correctly.

⚙️ Registered automatically via:
    edamorph/routes.py ➜ edamorph/backend/__init__.py ➜ this file
"""

from .routes import router  # ✅ Main APIRouter instance for settings module

# ✅ Explicitly declare public interface for this package
__all__ = ["router"]