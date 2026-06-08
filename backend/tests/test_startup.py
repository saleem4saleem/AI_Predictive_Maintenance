from __future__ import annotations

from fastapi import FastAPI

from app.main import app, create_app


def test_fastapi_app_imports_and_initializes() -> None:
    created_app = create_app()

    assert isinstance(app, FastAPI)
    assert isinstance(created_app, FastAPI)
    assert created_app.title


def test_docs_route_is_available(client) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_root_endpoint_points_to_health(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["health_url"] == "/api/v1/health"
