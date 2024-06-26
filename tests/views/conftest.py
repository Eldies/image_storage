import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import logic, storage_manager
from app.main import app
from app.settings import ClientInfo, S3Config, Settings


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch, mock_s3_bucket):
    # TODO: dynamically find all modules which use settings
    settings = Settings(
        clients_info={"0": ClientInfo(id="test_client", api_key="TEST_API_KEY")},
        s3=S3Config(
            bucket=mock_s3_bucket.name,
        ),
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
