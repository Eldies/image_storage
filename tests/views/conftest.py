import pytest
from flask.testing import FlaskClient


@pytest.fixture()
def client(settings, reset_fake_filesystem) -> FlaskClient:
    from app import create_app
    app = create_app({
        'TESTING': True,
    })
    with app.app_context():
        yield app.test_client()
