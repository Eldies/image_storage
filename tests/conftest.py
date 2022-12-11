# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch


@pytest.fixture()
def settings() -> None:
    from app.schemas import ClientInfo
    patches = [
        patch('app.settings.UPLOAD_FOLDER', '/test_upload_path'),
        patch('app.settings.CLIENTS_INFO', [ClientInfo(id='test_client', api_key='TEST_API_KEY')]),
    ]
    for p in patches:
        p.start()

    yield

    for p in patches:
        p.stop()


@pytest.fixture(autouse=True)
def reset_fake_filesystem(fs):
    fs.reset()


@pytest.fixture()
def no_fake_filesystem(fs):
    fs.pause()
    yield
    fs.resume()
