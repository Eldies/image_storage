# -*- coding: utf-8 -*-
import importlib

import pytest
from unittest.mock import patch

from app.types import ClientInfo
from app import settings


@pytest.mark.parametrize('folder', ['foo', 'bar'])
def test_upload_folder(folder):
    with patch('os.environ', dict(UPLOAD_FOLDER=folder)):
        importlib.reload(settings)
        assert settings.UPLOAD_FOLDER == folder


@pytest.mark.parametrize('env,var', [
    (dict(CLIENT_CREDENTIALS_1='cl:api_key1'), [ClientInfo('cl', 'api_key1')]),
    (dict(FOO='cl:api_key1'), []),
    (
        dict(
            CLIENT_CREDENTIALS_1='cl1:api_key3',
            CLIENT_CREDENTIALS_2='cl2:api_key2',
            CLIENT_CREDENTIALS_3='cl3:api_key1',
        ),
        [
            ClientInfo('cl1', 'api_key3'),
            ClientInfo('cl2', 'api_key2'),
            ClientInfo('cl3', 'api_key1'),
        ],
    ),
])
def test_client_info(env, var):
    with patch('os.environ', env):
        importlib.reload(settings)
        assert settings.CLIENTS_INFO == var
