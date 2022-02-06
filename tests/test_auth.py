# -*- coding: utf-8 -*-
import unittest
from json import JSONDecodeError

from auth import get_user_id_from_token


class TestGetUserIdFromToken(unittest.TestCase):
    def test_ok(self):
        assert get_user_id_from_token('{"id": 4}') == 4

    def test_cant_decode_token(self):
        with self.assertRaises(JSONDecodeError):
            get_user_id_from_token('garbage')

    def test_token_dict_does_not_contain_id(self):
        with self.assertRaises(KeyError):
            get_user_id_from_token('{"foo": "bar"}')
