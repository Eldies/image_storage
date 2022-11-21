# -*- coding: utf-8 -*-
import random
from unittest.mock import Mock, patch

import pytest

from app.logic import (
    generate_image_uuid,
    get_client_info_by_api_key,
)


@pytest.fixture()
def time_mock() -> Mock:
    mock = Mock(return_value=1657234419.0)
    with patch('time.time', mock):
        yield mock


class TestGetClientInfoByApiKey:
    @pytest.fixture(autouse=True)
    def _setup(self, settings):
        pass

    def test_ok(self):
        client = get_client_info_by_api_key('TEST_API_KEY')
        assert client.id == 'test_client'
        assert client.api_key == 'TEST_API_KEY'

    def test_wrong_api_key(self):
        client = get_client_info_by_api_key('random_string')
        assert client is None


class TestGenerateImageUUID:
    @pytest.fixture(autouse=True)
    def _setup(self, time_mock):
        self.time_mock = time_mock
        random.seed(0)

    def test_name(self):
        assert generate_image_uuid('FOO') == 'FOO-wRqkXu8ab9'

    def test_none(self):
        assert generate_image_uuid(None) == 'wRqkXu8ab9'

    def test_empty_string(self):
        assert generate_image_uuid('') == 'wRqkXu8ab9'

    def test_changes_with_millisecond(self):
        assert generate_image_uuid(None) == 'wRqkXu8ab9'
        self.time_mock.return_value += 0.001
        random.seed(0)
        assert generate_image_uuid(None) == 'wRqkXu8abA'
        # checking that it does not change just because of calling this function again
        random.seed(0)
        assert generate_image_uuid(None) == 'wRqkXu8abA'

    def test_changes_with_random(self):
        assert generate_image_uuid(None) == 'wRqkXu8ab9'
        random.seed(1)
        assert generate_image_uuid(None) == '9dwkXu8ab9'
        # checking that it does not change just because of calling this function again
        random.seed(1)
        assert generate_image_uuid(None) == '9dwkXu8ab9'
