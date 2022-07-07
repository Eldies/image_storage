# -*- coding: utf-8 -*-
from app.logic import get_client_info_by_api_key


class TestGetClientInfoByApiKey:
    def test_ok(self):
        client = get_client_info_by_api_key('TEST_API_KEY')
        assert client.id == 'test_client'
        assert client.api_key == 'TEST_API_KEY'

    def test_wrong_api_key(self):
        client = get_client_info_by_api_key('random_string')
        assert client is None
