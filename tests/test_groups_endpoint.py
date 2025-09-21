import pytest
from httpx import ASGITransport, AsyncClient

from app_init import app


@pytest.mark.asyncio
async def test_create_group(unique_name):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/groups", json={"name": unique_name})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == unique_name
        assert data["status"] == "created"
        assert "id" in data


@pytest.mark.asyncio
async def test_get_all_groups():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/groups")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_group_by_id(unique_name):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post("/api/groups", json={"name": unique_name})
        assert create_response.status_code == 200
        group_id = create_response.json()["id"]

        response = await client.get(f"/api/groups/{group_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == unique_name
        assert data["id"] == group_id


@pytest.mark.asyncio
async def test_get_nonexistent_group():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/groups/99999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_group(unique_name):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post("/api/groups", json={"name": unique_name})
        assert create_response.status_code == 200
        group_id = create_response.json()["id"]

        delete_response = await client.delete(f"/api/groups/{group_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == "deleted"

        get_response = await client.get(f"/api/groups/{group_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_group():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/api/groups/99999")
        assert response.status_code == 404