# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest

from app.schemas import ClientInfo
from app.settings import get_settings


@pytest.mark.parametrize("folder", ["foo", "bar"])
def test_upload_folder(folder):
    with patch("os.environ", dict(UPLOAD_FOLDER=folder)):
        assert get_settings().upload_folder == folder


@pytest.mark.parametrize(
    "env,var",
    [
        (
            dict(CLIENTS_INFO__0__api_key="api_key1", CLIENTS_INFO__0__id="cl"),
            {"0": ClientInfo("cl", "api_key1")},
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
                "0": ClientInfo("cl1", "api_key3"),
                "1": ClientInfo("cl2", "api_key2"),
                "2": ClientInfo("cl3", "api_key1"),
            },
        ),
    ],
)
def test_client_info(env, var):
    with patch("os.environ", env):
        assert get_settings().clients_info == var
