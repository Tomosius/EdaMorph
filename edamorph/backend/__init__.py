"""
📁 edamorph.backend.__init__.py

🔧 Dynamic router discovery and aggregation system.

This module automatically finds all submodules inside the `backend/` folder
that expose a `router` object (typically a FastAPI `APIRouter`) and collects them.

✅ Benefits:
- Keeps your `routes.py` file clean and DRY (Don't Repeat Yourself).
- Supports plug-and-play modularity: just drop a folder with a `routes.py` file that defines `router`.
- Automatically includes new routes without manual import maintenance.

🎯 Usage:
In your main `routes.py`, you can do:
    from edamorph.backend import routers
    for r in routers:
        app.include_router(r)

⚠️ Assumes each backend submodule exposes a top-level `router` object.
"""

import pkgutil  # 🔍 For discovering submodules inside a package
from importlib import import_module  # 🧠 Dynamically import modules

# ✅ List to collect all discovered routers
routers = []

# 🔍 Discover all submodules (folders/files) under this package's path
# __path__ is a special attribute that exists only in __init__.py of a package
_submodules = [name for _, name, _ in pkgutil.iter_modules(__path__)]

# 🔁 Iterate through each discovered submodule
for name in _submodules:
    # 🔗 Dynamically import the submodule (e.g., backend.app_settings)
    module = import_module(f"{__name__}.{name}")

    # ✅ Check if the submodule has a `router` attribute (typically from routes.py)
    if hasattr(module, "router"):
        # ➕ Append the router to the global list
        routers.append(module.router)