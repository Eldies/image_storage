# -*- coding: utf-8 -*-
import unittest
from unittest.mock import Mock, patch

from auth import (
    check_api_key,
    InvalidApiKey,
)


class TestGetUserIdFromToken(unittest.TestCase):
    def test_ok(self):
        with patch('settings.CLIENT_API_KEY', 'TEST_API_KEY'):
            check_api_key('TEST_API_KEY')

    def test_wrong_api_key(self):
        with patch('settings.CLIENT_API_KEY', 'TEST_API_KEY'):
            with self.assertRaises(InvalidApiKey):
                check_api_key('random_string')
