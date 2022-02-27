# -*- coding: utf-8 -*-
import io
import logging
import unittest
from unittest.mock import Mock, patch

from app import app
from auth import get_user_id_from_token
from storage_manager import StorageManager


class TestImageView(unittest.TestCase):
    def setUp(self):
        app.logger.setLevel(logging.DEBUG)
        app.config['TESTING'] = True
        self.client = app.test_client()

        self.get_user_mock = Mock(wraps=get_user_id_from_token)
        self.image_storage_mock = Mock(spec=StorageManager)
        self.image_storage_mock.return_value.uuid_exists.return_value = False
        self.uuid4_mock = Mock()
        self.uuid4_mock.return_value = 'random_uuid'

        self.patches = [
            patch('views.get_user_id_from_token', self.get_user_mock),
            patch('views.StorageManager', self.image_storage_mock),
            patch('views.uuid.uuid4', self.uuid4_mock),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_post_no_token(self):
        response = self.client.post('/v1/image/')
        assert self.get_user_mock.call_count == 0
        assert response.status_code == 401
        assert response.json == {'error': 'Token not provided'}

    def test_post_token_wo_user_id(self):
        response = self.client.post('/v1/image/', headers={'Authorization': 'Bearer {"foo": "bar"}'})
        assert self.get_user_mock.call_count == 1
        assert self.get_user_mock.call_args.args == ('{"foo": "bar"}',)
        assert response.status_code == 403
        assert response.json == {'error': 'Invalid token'}

    def test_post_no_file(self):
        response = self.client.post('/v1/image/', headers={'Authorization': 'Bearer {"id": 123456}'})
        assert self.get_user_mock.call_count == 1
        assert self.get_user_mock.call_args.args == ('{"id": 123456}',)
        assert response.status_code == 400
        assert response.json == {'error': 'No file'}

    def test_post_ok(self):
        data = {
            'some_key': 'some_data',
            'file': (io.BytesIO(b'abcdef'), 'test.jpg'),
        }
        response = self.client.post(
            '/v1/image/',
            headers={'Authorization': 'Bearer {"id": 123456}'},
            data=data,
            content_type='multipart/form-data',
        )
        assert self.get_user_mock.call_count == 1
        assert self.get_user_mock.call_args.args == ('{"id": 123456}',)
        assert self.image_storage_mock.call_count == 1
        assert self.image_storage_mock.return_value.uuid_exists.call_count == 1
        assert self.image_storage_mock.return_value.save_image.call_count == 1
        assert response.status_code == 200
        assert response.json == {'status': 'ok', 'uuid': 'random_uuid'}
