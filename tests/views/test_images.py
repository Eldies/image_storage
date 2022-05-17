# -*- coding: utf-8 -*-
import base64
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

    def check_ok_request(self, additional_data, filename_in_address=None, filename_in_form=None, make_json=False, _base64=False):
        data = dict(**additional_data)
        if _base64:
            data['base64'] = base64.b64encode(b'abcdef').decode()
        else:
            data['file'] = (io.BytesIO(b'abcdef'), 'test.jpg')
        if filename_in_form:
            data['filename'] = filename_in_form
            additional_data['filename'] = filename_in_form
        expected_filename = (filename_in_address or filename_in_form or 'MTIzN') + '-MDk4NzY1NDMyMTA5ODc2NQ'
        response = self.client.post(
            '/v1/image/{}'.format(filename_in_address or ''),
            headers={'X-API-KEY': 'TEST_API_KEY'},
            data=json.dumps(data) if make_json else data,
            content_type='application/json' if make_json else 'multipart/form-data',
        )
        assert self.image_storage_mock.call_count == 1
        assert self.image_storage_mock.return_value.save_image.call_count == 1
        save_image_call_args = self.image_storage_mock.return_value.save_image.call_args.args
        assert save_image_call_args[0] == expected_filename
        assert save_image_call_args[1] == b'abcdef'
        assert json.loads(save_image_call_args[2]) == dict(
            data=additional_data,
            mimetype='image/jpeg',
            content_length=6,
        )
        assert response.status_code == 200
        assert response.json == {
            'status': 'ok',
            'uuid': expected_filename,
        }

    def test_post_ok(self):
        self.check_ok_request({})

    def test_post_ok_base64(self):
        self.check_ok_request({}, _base64=True)

    def test_post_ok_json(self):
        self.check_ok_request({}, make_json=True, _base64=True)

    def test_post_ok_json_with_filename(self):
        self.check_ok_request({}, make_json=True, _base64=True, filename_in_form='filename')

    def test_post_ok_json_with_some_key(self):
        self.check_ok_request({'foo': 'bar'}, make_json=True, _base64=True)

    def test_post_ok_with_filename(self):
        self.check_ok_request({}, filename_in_address='filename')

    def test_post_ok_with_filename_in_form(self):
        self.check_ok_request({}, filename_in_form='filename')

    def test_post_ok_with_some_data(self):
        self.check_ok_request({'some_key': 'some_data'})

    def test_post_empty_file(self):
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

    def test_get_ok(self):
        self.image_storage_mock.return_value.uuid_exists.return_value = True
        self.image_storage_mock.return_value.read_file.return_value = io.BytesIO(b'abcdef')
        self.image_storage_mock.return_value.read_data.return_value = '{"mimetype": "image/jpeg"}'
        response = self.client.get('/v1/image/some_uuid')
        assert response.status_code == 200
        assert response.content_type == 'image/jpeg'
        assert response.data == b'abcdef'

    def test_get_unknown_uuid(self):
        response = self.client.get('/v1/image/some_uuid')
        assert response.status_code == 404
