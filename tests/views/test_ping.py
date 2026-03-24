# -*- coding: utf-8 -*-
import pytest


@pytest.mark.asyncio
class TestPingView:
    async def test_ping(self, client):
        response = await client.get("/ping")
        assert response.status_code == 200
        assert response.content == b'"pong"'
