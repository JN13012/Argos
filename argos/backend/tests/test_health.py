import pytest
from argos.backend.api.main import create_app
from argos.backend.core.config import Settings
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_health_reports_only_service_status() -> None:
    app = create_app(Settings(_env_file=None))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_unknown_routes_use_the_stable_error_shape() -> None:
    app = create_app(Settings(_env_file=None))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/api/v1/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "http_error", "message": "Not Found"}
    }


@pytest.mark.anyio
async def test_post_to_health_is_not_an_allowed_operation() -> None:
    app = create_app(Settings(_env_file=None))
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/api/v1/health", json={"secret": "not-returned"}
        )

    assert response.status_code == 405
    assert response.json() == {
        "error": {"code": "http_error", "message": "Method Not Allowed"}
    }
    assert "not-returned" not in response.text
