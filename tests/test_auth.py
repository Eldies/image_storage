# -*- coding: utf-8 -*-
import unittest

from auth import (
    get_user_id_from_token,
    InvalidTokenError,
    TokenDoesNotHaveIdError,
)


class TestGetUserIdFromToken(unittest.TestCase):
    def test_ok(self):
        assert get_user_id_from_token('{"id": 4}') == 4

    def test_cant_decode_token(self):
        with self.assertRaises(InvalidTokenError):
            get_user_id_from_token('garbage')

    def test_token_dict_does_not_contain_id(self):
        with self.assertRaises(TokenDoesNotHaveIdError):
            get_user_id_from_token('{"foo": "bar"}')
