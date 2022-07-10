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


@pytest.mark.parametrize('api_key', ['api_key1', 'api_key2'])
def test_client_info(api_key):
    with patch('os.environ', dict(CLIENT_API_KEY=api_key)):
        importlib.reload(settings)
        assert settings.CLIENTS_INFO == [
            ClientInfo('toysdb', api_key),
        ]
