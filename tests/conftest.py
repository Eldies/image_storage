# -*- coding: utf-8 -*-
from flask import Flask
from flask.testing import FlaskClient

import pytest
from unittest.mock import (
    Mock,
    patch,
)

from app import create_app
from app.storage_manager import StorageManager
from app.types import ClientInfo


@pytest.fixture(autouse=True)
def settings() -> None:
    patches = [
        patch('app.settings.UPLOAD_FOLDER', 'test_upload_path'),
        patch('app.settings.CLIENTS_INFO', [ClientInfo(id='test_client', api_key='TEST_API_KEY')]),
    ]
    for p in patches:
        p.start()

    yield

    for p in patches:
        p.stop()


@pytest.fixture()
def app() -> Flask:
    app = create_app({
        'TESTING': True,
    })
    with app.app_context():
        yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def random_choice_mock() -> Mock:
    mock = Mock(return_value='a')
    with patch('random.choice', mock):
        yield mock


@pytest.fixture()
def time_mock() -> Mock:
    mock = Mock(return_value=1657234419.0)
    with patch('time.time', mock):
        yield mock


@pytest.fixture()
def image_storage_mock() -> Mock:
    mock = Mock(spec=StorageManager)
    mock.return_value.uuid_exists.return_value = False
    with patch('app.views.StorageManager', mock):
        yield mock


@pytest.fixture()
def environment(
        time_mock,
        random_choice_mock,
        image_storage_mock,
):
    class Environment:
        def __init__(self):
            self.time_mock = time_mock
            self.random_choice_mock = random_choice_mock
            self.image_storage_mock = image_storage_mock

    return Environment()
