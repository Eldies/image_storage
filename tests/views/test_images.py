# -*- coding: utf-8 -*-
import io
import json
import logging
import unittest
import uuid
from unittest.mock import Mock, patch

from app import app
from storage_manager import StorageManager


class TestImageView(unittest.TestCase):
    def setUp(self):
        app.logger.setLevel(logging.DEBUG)
        app.config['TESTING'] = True
        self.client = app.test_client()

        self.image_storage_mock = Mock(spec=StorageManager)
        self.image_storage_mock.return_value.uuid_exists.return_value = False
        self.uuid_mock = Mock(
            uuid1=Mock(return_value=uuid.UUID(bytes=b'0987654321098765')),
            uuid4=Mock(return_value=uuid.UUID(bytes=b'1234567890123456')),
        )

        self.patches = [
            patch('settings.CLIENT_API_KEY', 'TEST_API_KEY'),
            patch('views.StorageManager', self.image_storage_mock),
            patch('views.uuid', self.uuid_mock),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_post_no_api_key(self):
        response = self.client.post('/v1/image/')
        assert response.status_code == 401
        assert response.json == {'status': 'error', 'error': 'Unauthorized'}

    def test_post_wrong_api_key(self):
        response = self.client.post('/v1/image/', headers={'X-API-KEY': 'random_string'})
        assert response.status_code == 403
        assert response.json == {'status': 'error', 'error': 'Invalid api key'}

    def test_post_no_file(self):
        response = self.client.post('/v1/image/', headers={'X-API-KEY': 'TEST_API_KEY'})
        assert response.status_code == 400
        assert response.json == {'status': 'error', 'error': 'No file'}

    def check_ok_request(self, additional_data, filename=None):
        data = dict(
            file=(io.BytesIO(b'abcdef'), 'test.jpg'),
            **additional_data
        )
        response = self.client.post(
            '/v1/image/{}'.format(filename or ''),
            headers={'X-API-KEY': 'TEST_API_KEY'},
            data=data,
            content_type='multipart/form-data',
        )
        assert self.image_storage_mock.call_count == 1
        assert self.image_storage_mock.return_value.save_image.call_count == 1
        save_image_call_args = self.image_storage_mock.return_value.save_image.call_args.args
        assert json.loads(save_image_call_args[2]) == dict(
            data=additional_data,
            mimetype='image/jpeg',
            content_length=6,
        )
        assert response.status_code == 200
        assert response.json == {
            'status': 'ok',
            'uuid': (filename if filename else 'MTIzN') + '-MDk4NzY1NDMyMTA5ODc2NQ',
        }

    def test_post_ok(self):
        self.check_ok_request({})

    def test_post_ok_with_filename(self):
        self.check_ok_request({}, filename='filename')

    def test_post_ok_with_some_data(self):
        self.check_ok_request({'some_key': 'some_data'})

    def test_read_image(self):
        self.image_storage_mock.return_value.uuid_exists.return_value = True
        self.image_storage_mock.return_value.read_file.return_value = io.BytesIO(b'abcdef')
        self.image_storage_mock.return_value.read_data.return_value = '{"mimetype": "image/jpeg"}'
        response = self.client.get('/v1/image/some_uuid')
        assert response.status_code == 200
        assert response.content_type == 'image/jpeg'
        assert response.data == b'abcdef'

    def test_read_image_unknown_uuid(self):
        response = self.client.get('/v1/image/some_uuid')
        assert response.status_code == 404

    def test_empty_file(self):
        data = dict(
            file=(io.BytesIO(b''), 'test.jpg'),
        )
        response = self.client.post(
            '/v1/image/',
            headers={'X-API-KEY': 'TEST_API_KEY'},
            data=data,
            content_type='multipart/form-data',
        )
        assert response.status_code == 400
        assert response.json == {'status': 'error', 'error': 'Empty file'}
