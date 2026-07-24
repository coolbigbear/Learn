"""Tests for the admin router (re-seed endpoint)."""

import os

import pytest
from httpx import AsyncClient

# Ensure we use the test database
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")


class TestAdminReSeed:
    """Integration tests for the POST /api/admin/re-seed endpoint."""

    @pytest.mark.asyncio
    async def test_re_seed_requires_auth(self, client: AsyncClient):
        """Re-seed should return 401 without authentication."""
        resp = await client.post("/api/admin/re-seed")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_re_seed_forbidden_for_non_admin(self, client: AsyncClient):
        """Re-seed should return 403 for non-admin users."""
        # Register a regular user
        resp = await client.post(
            "/api/auth/register",
            json={"username": "regularuser", "password": "testpass123"},
        )
        assert resp.status_code == 201
        token = resp.json()["token"]

        # Try to re-seed
        resp = await client.post(
            "/api/admin/re-seed",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
        assert "Only administrators" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_re_seed_allowed_for_developer(self, client: AsyncClient):
        """Re-seed should work for the 'developer' user."""
        # Register as developer
        resp = await client.post(
            "/api/auth/register",
            json={"username": "developer", "password": "devprofile"},
        )
        assert resp.status_code == 201
        token = resp.json()["token"]

        # Re-seed should succeed
        resp = await client.post(
            "/api/admin/re-seed",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "reimported"
        assert "lessons_added" in data
        assert "exercises_added" in data

    @pytest.mark.asyncio
    async def test_re_seed_allowed_for_admin(self, client: AsyncClient):
        """Re-seed should work for the 'admin' user."""
        # Register as admin
        resp = await client.post(
            "/api/auth/register",
            json={"username": "admin", "password": "adminpass123"},
        )
        assert resp.status_code == 201
        token = resp.json()["token"]

        # Re-seed should succeed
        resp = await client.post(
            "/api/admin/re-seed",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "reimported"
        assert "lessons_added" in data
