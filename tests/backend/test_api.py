import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_list_jobs_empty(client: AsyncClient):
    response = await client.get("/api/jobs")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_job_not_found(client: AsyncClient):
    response = await client.get("/api/jobs/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_results_not_found(client: AsyncClient):
    response = await client.get("/api/results/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_upload_invalid_file_type(client: AsyncClient):
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = await client.post("/api/videos/upload", files=files)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
