# -*- coding: utf-8 -*-
import pytest
import pytest_asyncio


@pytest.mark.asyncio
class TestPingView:
    @pytest_asyncio.fixture(autouse=True)
    def _setup(self, client):
        self.client = client

    async def test_ping(self):
        response = await self.client.get("/ping")
        assert response.status_code == 200
        assert response.content == b'"pong"'
