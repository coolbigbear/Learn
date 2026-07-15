"""Tests for the version endpoint."""

from httpx import AsyncClient


class TestVersion:
    async def test_version_returns_expected(self, client: AsyncClient):
        resp = await client.get("/api/version")
        assert resp.status_code == 200
        data = resp.json()
        assert "version" in data
        assert data["version"] == "0.1.0"

    async def test_version_no_auth_required(self, client: AsyncClient):
        """Version endpoint should not require authentication."""
        resp = await client.get("/api/version")
        assert resp.status_code == 200

    async def test_version_response_shape(self, client: AsyncClient):
        """Version endpoint should return the expected JSON shape."""
        resp = await client.get("/api/version")
        data = resp.json()
        assert list(data.keys()) == ["version"]
        assert isinstance(data["version"], str)