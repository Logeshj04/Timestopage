import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success_and_me(client: AsyncClient):
    response = await client.post("/api/auth/login", json={"username": "admin", "password": "AdminPass123!"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["role"] == "admin"


@pytest.mark.asyncio
async def test_login_invalid_is_generic(client: AsyncClient):
    response = await client.post("/api/auth/login", json={"username": "nobody", "password": "wrong"})
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_protected_route_requires_auth(client: AsyncClient):
    response = await client.get("/api/stoppages")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_supervisor_cannot_manage_users(client: AsyncClient):
    login = await client.post("/api/auth/login", json={"username": "supera", "password": "SuperPass123!"})
    token = login.json()["access_token"]
    response = await client.get("/api/auth/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
