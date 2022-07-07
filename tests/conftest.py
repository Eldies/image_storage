# -*- coding: utf-8 -*-
import uuid

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


@pytest.fixture()
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
def app(settings) -> Flask:
    app = create_app({
        'TESTING': True,
    })
    with app.app_context():
        yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


class Environment:
    def __init__(self):
        self.image_storage_mock = Mock(spec=StorageManager)
        self.image_storage_mock.return_value.uuid_exists.return_value = False
        self.uuid_mock = Mock(
            uuid1=Mock(return_value=uuid.UUID(bytes=b'0987654321098765')),
            uuid4=Mock(return_value=uuid.UUID(bytes=b'1234567890123456')),
        )

        self.patches = [
            patch('app.views.StorageManager', self.image_storage_mock),
            patch('app.views.uuid', self.uuid_mock),
        ]

    def __enter__(self):
        for p in self.patches:
            p.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        for p in self.patches:
            p.stop()


@pytest.fixture()
def environment() -> Environment:
    env = Environment()
    with env:
        yield env
