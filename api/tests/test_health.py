"""Tests for the health check endpoint and general API behavior."""
from httpx import AsyncClient


class TestHealth:
    async def test_health_returns_ok(self, client: AsyncClient):
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert "database" in body  # New: database info included

    async def test_health_no_auth_required(self, client: AsyncClient):
        """Health endpoint should not require authentication."""
        resp = await client.get("/api/health")
        assert resp.status_code == 200

    async def test_health_database_tables(self, client: AsyncClient):
        """Health endpoint should report table count."""
        resp = await client.get("/api/health")
        body = resp.json()
        assert body["database"]["tables"] >= 4  # users, lessons, exercises, user_progress