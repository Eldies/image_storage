from typing import Any, AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import storage_manager
from app.main import app
from app.settings import ClientInfo


@pytest_asyncio.fixture()
async def client(mock_settings, mock_s3_bucket) -> AsyncGenerator[AsyncClient, Any]:
    storage_manager.get_storage_manager.cache_clear()
    mock_settings.storage.s3.bucket = mock_s3_bucket.name
    mock_settings.clients_info["0"] = ClientInfo(id="test_client", api_key="TEST_API_KEY")
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
