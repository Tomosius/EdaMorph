# tests/test_routes.py

"""
🧪 Test suite for edamorph.routes

Verifies:
- APIRouter is created
- Submodule routers are registered
- Routes are unique and accessible
"""

import pytest
from fastapi import APIRouter, FastAPI
from starlette.testclient import TestClient
from fastapi.staticfiles import StaticFiles
from edamorph.routes import router
from pathlib import Path


def test_router_is_instance_of_apirouter():
    """Ensure router is a FastAPI APIRouter."""
    assert isinstance(router, APIRouter), "router is not an instance of APIRouter"


def test_router_has_registered_routes():
    """Ensure at least one route is registered."""
    assert router.routes, "No routes have been registered in the global router"


@pytest.mark.parametrize("route", [r for r in router.routes])
def test_each_route_has_required_fields(route):
    """Check that each route has a path and method."""
    assert hasattr(route, "path")
    assert hasattr(route, "methods")
    assert route.path.startswith("/"), f"Invalid route path: {route.path}"


def test_route_paths_are_unique():
    """Ensure all route paths are unique per method."""
    seen = set()
    for route in router.routes:
        for method in route.methods:
            key = (route.path, method)
            assert key not in seen, f"Duplicate route: {route.path} [{method}]"
            seen.add(key)


def test_router_integrates_with_fastapi():
    """Mount the router to a FastAPI app and check for basic accessibility."""
    app = FastAPI()

    # ✅ Ensure static mount uses absolute path to avoid test failures
    static_dir = Path(__file__).parent / "assets"
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

    app.include_router(router)
    client = TestClient(app)

    # Try GET on all GET routes without path params
    for route in router.routes:
        if "GET" in route.methods and "{" not in route.path:
            response = client.get(route.path)
            assert response.status_code in (200, 302, 404), (
                f"Route {route.path} returned unexpected status {response.status_code}"
            )