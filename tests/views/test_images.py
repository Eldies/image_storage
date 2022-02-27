# -*- coding: utf-8 -*-
import io
import json
import logging
import unittest
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
        self.uuid4_mock = Mock(return_value='random_uuid')

        self.patches = [
            patch('settings.CLIENT_API_KEY', 'TEST_API_KEY'),
            patch('views.StorageManager', self.image_storage_mock),
            patch('views.uuid.uuid4', self.uuid4_mock),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_post_no_api_key(self):
        response = self.client.post('/v1/image/')
        assert response.status_code == 401
        assert response.json == {'error': 'Unauthorized'}

    def test_post_wrong_api_key(self):
        response = self.client.post('/v1/image/', headers={'X-API-KEY': 'random_string'})
        assert response.status_code == 403
        assert response.json == {'error': 'Invalid api key'}

    def test_post_no_file(self):
        response = self.client.post('/v1/image/', headers={'X-API-KEY': 'TEST_API_KEY'})
        assert response.status_code == 400
        assert response.json == {'error': 'No file'}

    def check_ok_request(self, additional_data, uuid_exists_call_count=1):
        data = dict(
            file=(io.BytesIO(b'abcdef'), 'test.jpg'),
            **additional_data
        )
        response = self.client.post(
            '/v1/image/',
            headers={'X-API-KEY': 'TEST_API_KEY'},
            data=data,
            content_type='multipart/form-data',
        )
        assert self.image_storage_mock.call_count == 1
        assert self.image_storage_mock.return_value.uuid_exists.call_count == uuid_exists_call_count
        assert self.image_storage_mock.return_value.save_image.call_count == 1
        save_image_call_args = self.image_storage_mock.return_value.save_image.call_args.args
        assert json.loads(save_image_call_args[2]) == dict(
            data=additional_data,
            mimetype='image/jpeg',
        )
        assert response.status_code == 200
        assert response.json == {'status': 'ok', 'uuid': 'random_uuid'}

    def test_post_ok(self):
        self.check_ok_request({})

    def test_post_ok_generated_existing_uuid(self):
        self.image_storage_mock.return_value.uuid_exists.side_effect = [True, True, False]
        self.check_ok_request({}, uuid_exists_call_count=3)

    def test_post_ok_with_some_data(self):
        self.check_ok_request({'some_key': 'some_data'})
