# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest

from app.settings import ClientInfo, Settings


@pytest.mark.parametrize(
    "env,clients",
    [
        (
            dict(CLIENTS__cl__api_key="api_key1"),
            [ClientInfo(id="cl", api_key="api_key1")],
        ),
        (dict(), []),
        (
            dict(
                CLIENTS__cl1__api_key="api_key3",
                CLIENTS__cl2__api_key="api_key2",
                CLIENTS__cl3__api_key="api_key1",
            ),
            [
                ClientInfo(id="cl1", api_key="api_key3"),
                ClientInfo(id="cl2", api_key="api_key2"),
                ClientInfo(id="cl3", api_key="api_key1"),
            ],
        ),
    ],
)
def test_client_info(env, clients):
    with patch("os.environ", env):
        assert Settings().clients.by_id == {client.id: client for client in clients}
        assert Settings().clients.by_api_key == {client.api_key: client for client in clients}
