import pytest_asyncio
from httpx import AsyncClient
from app import app


@pytest_asyncio.fixture()
async def client(settings, reset_fake_filesystem) -> AsyncClient:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
    ) as client:
        yield client
