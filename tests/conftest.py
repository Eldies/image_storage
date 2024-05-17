# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch
import tempfile


@pytest.fixture()
def upload_folder() -> str:
    return tempfile.mkdtemp()


@pytest.fixture()
def settings(upload_folder: str) -> None:
    from app.schemas import ClientInfo
    patches = [
        patch('app.settings.UPLOAD_FOLDER', upload_folder),
        patch('app.settings.CLIENTS_INFO', [ClientInfo(id='test_client', api_key='TEST_API_KEY')]),
    ]
    for p in patches:
        p.start()

    yield

    for p in patches:
        p.stop()
