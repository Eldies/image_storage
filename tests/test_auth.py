# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from app.auth import get_client_info_by_api_key
from app.settings import ClientInfo


class TestGetUserIdFromToken(unittest.TestCase):
    def test_ok(self):
        with patch('app.settings.CLIENTS_INFO', [ClientInfo(id='test_client', api_key='TEST_API_KEY')]):
            client = get_client_info_by_api_key('TEST_API_KEY')
            assert client.id == 'test_client'
            assert client.api_key == 'TEST_API_KEY'

    def test_wrong_api_key(self):
        with patch('app.settings.CLIENTS_INFO', [ClientInfo(id='test_client', api_key='TEST_API_KEY')]):
            client = get_client_info_by_api_key('random_string')
            assert client is None
