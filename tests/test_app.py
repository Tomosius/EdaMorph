# tests/test_app.py

from fastapi.testclient import TestClient
from edamorph.app import app


def test_root_endpoint_renders_template():
    """Ensure the root (/) route renders HTML with 200 status."""
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<html" in response.text.lower()  # Rough check for template render


def test_openapi_docs_available():
    """Check if OpenAPI schema and docs are available."""
    client = TestClient(app)

    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text

    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "EdaMorph"