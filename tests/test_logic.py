# -*- coding: utf-8 -*-
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
    def _setup(self, uuid_mock):
        self.uuid_mock = uuid_mock

    def test_name(self):
        uuid = generate_image_uuid('FOO')
        assert uuid == 'FOO-MDk4NzY1NDMyMTA5ODc2NQ'

    def test_none(self):
        uuid = generate_image_uuid(None)
        assert uuid == 'MTIzN-MDk4NzY1NDMyMTA5ODc2NQ'

    def test_empty_string(self):
        uuid = generate_image_uuid('')
        assert uuid == 'MTIzN-MDk4NzY1NDMyMTA5ODc2NQ'
