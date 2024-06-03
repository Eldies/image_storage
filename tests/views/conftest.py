import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import app, logic, storage_manager
from app.settings import ClientInfo, Settings


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch, upload_folder):
    # TODO: dynamically find all modules which use settings
    settings = Settings(
        clients_info={"0": ClientInfo(id="test_client", api_key="TEST_API_KEY")},
        upload_folder=upload_folder,
    )
    monkeypatch.setattr(logic, "settings", settings)
    monkeypatch.setattr(storage_manager, "settings", settings)


@pytest_asyncio.fixture()
async def client(mock_settings) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
