# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest

from app.settings import Settings


@pytest.mark.parametrize(
    "env,clients_info",
    [
        (
            dict(CLIENTS_INFO__0__api_key="api_key1", CLIENTS_INFO__0__id="cl"),
            {"0": dict(id="cl", api_key="api_key1")},
        ),
        (dict(), {}),
        (
            dict(
                CLIENTS_INFO__0__api_key="api_key3",
                CLIENTS_INFO__0__id="cl1",
                CLIENTS_INFO__1__api_key="api_key2",
                CLIENTS_INFO__1__id="cl2",
                CLIENTS_INFO__2__api_key="api_key1",
                CLIENTS_INFO__2__id="cl3",
            ),
            {
                "0": dict(id="cl1", api_key="api_key3"),
                "1": dict(id="cl2", api_key="api_key2"),
                "2": dict(id="cl3", api_key="api_key1"),
            },
        ),
    ],
)
def test_client_info(env, clients_info):
    with patch("os.environ", env):
        parsed_clients_info = {key: dict(value) for key, value in Settings().clients_info.items()}
        assert parsed_clients_info == clients_info
