# -*- coding: utf-8 -*-
import uuid

import pytest

from app.logic import (
    generate_image_uuid,
    get_client_info_by_api_key,
)


class TestGetClientInfoByApiKey:
    def test_ok(self):
        client = get_client_info_by_api_key('TEST_API_KEY')
        assert client.id == 'test_client'
        assert client.api_key == 'TEST_API_KEY'

    def test_wrong_api_key(self):
        client = get_client_info_by_api_key('random_string')
        assert client is None


class TestGenerateImageUUID:
    @pytest.fixture(autouse=True)
    def _setup(self, uuid_mock, time_mock):
        self.uuid_mock = uuid_mock
        self.time_mock = time_mock

    def test_name(self):
        assert generate_image_uuid('FOO') == 'FOO-75MkXu8ab9'

    def test_none(self):
        assert generate_image_uuid(None) == '75MkXu8ab9'

    def test_empty_string(self):
        assert generate_image_uuid('') == '75MkXu8ab9'

    def test_changes_with_millisecond(self):
        assert generate_image_uuid(None) == '75MkXu8ab9'
        self.time_mock.return_value += 0.001
        assert generate_image_uuid(None) == '75MkXu8abA'
        # checking that it does not change just because of calling this function again
        assert generate_image_uuid(None) == '75MkXu8abA'

    def test_changes_with_random(self):
        assert generate_image_uuid(None) == '75MkXu8ab9'
        self.uuid_mock.uuid4.return_value = uuid.UUID(bytes=b'9876543210987654')
        assert generate_image_uuid(None) == '84pkXu8ab9'
        # checking that it does not change just because of calling this function again
        assert generate_image_uuid(None) == '84pkXu8ab9'
