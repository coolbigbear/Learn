"""Tests for auth endpoints: register, login, logout."""

from httpx import AsyncClient


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"username": "alice", "password": "secret1234"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["username"] == "alice"
        assert "id" in body
        assert "token" in body
        assert len(body["token"]) > 20

    async def test_register_duplicate_username(self, client: AsyncClient):
        await client.post(
            "/api/auth/register",
            json={"username": "alice", "password": "secret1234"},
        )
        resp = await client.post(
            "/api/auth/register",
            json={"username": "alice", "password": "otherpass"},
        )
        assert resp.status_code == 409
        assert "already taken" in resp.json()["detail"].lower()

    async def test_register_validation_short_username(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"username": "a", "password": "secret1234"},
        )
        assert resp.status_code == 422

    async def test_register_validation_short_password(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/register",
            json={"username": "bob", "password": "ab"},
        )
        assert resp.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient):
        # Register first
        await client.post(
            "/api/auth/register",
            json={"username": "bob", "password": "mypassword"},
        )
        # Login
        resp = await client.post(
            "/api/auth/login",
            json={"username": "bob", "password": "mypassword"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["username"] == "bob"
        assert "token" in body
        assert len(body["token"]) > 20

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post(
            "/api/auth/register",
            json={"username": "bob", "password": "mypassword"},
        )
        resp = await client.post(
            "/api/auth/login",
            json={"username": "bob", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/login",
            json={"username": "nobody", "password": "somepass"},
        )
        assert resp.status_code == 401


class TestLogout:
    async def test_logout_success(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/auth/logout", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["detail"] == "Logged out"

    async def test_logout_without_token(self, client: AsyncClient):
        resp = await client.post("/api/auth/logout")
        assert resp.status_code == 401

    async def test_logout_invalid_token(self, client: AsyncClient):
        resp = await client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert resp.status_code == 401


class TestProfile:
    async def test_get_me_success(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["username"] == "testuser"
        assert "id" in body
        assert "created_at" in body

    async def test_get_me_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer bad-token"},
        )
        assert resp.status_code == 401
