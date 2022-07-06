# -*- coding: utf-8 -*-
from flask import Flask
from flask.testing import FlaskClient

import pytest
from unittest.mock import patch

from app import create_app
from app.settings import ClientInfo


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
def app() -> Flask:
    app = create_app({
        'TESTING': True,
    })
    with app.app_context():
        yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()
