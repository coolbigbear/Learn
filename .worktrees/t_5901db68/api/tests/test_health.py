"""Tests for the health check endpoint and general API behavior."""
from httpx import AsyncClient


class TestHealth:
    async def test_health_returns_ok(self, client: AsyncClient):
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    async def test_health_no_auth_required(self, client: AsyncClient):
        """Health endpoint should not require authentication."""
        resp = await client.get("/api/health")
        assert resp.status_code == 200