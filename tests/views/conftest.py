import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app import app


@pytest_asyncio.fixture()
async def client(monkeypatch) -> AsyncClient:
    monkeypatch.setenv("CLIENTS_INFO__0__api_key", "TEST_API_KEY")
    monkeypatch.setenv("CLIENTS_INFO__0__id", "test_client")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
