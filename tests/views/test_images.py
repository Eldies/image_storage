# -*- coding: utf-8 -*-
import base64
import io
import json

import pytest


class TestImageView:
    @pytest.fixture(autouse=True)
    def _setup(self, client, environment):
        self.client = client
        self.env = environment

    def test_post_no_api_key(self):
        response = self.client.post('/v1/image/')
        assert response.status_code == 401
        assert response.json == {'status': 'error', 'error': 'Unauthorized'}

    def test_post_wrong_api_key(self):
        response = self.client.post('/v1/image/', headers={'X-API-KEY': 'random_string'})
        assert response.status_code == 401
        assert response.json == {'status': 'error', 'error': 'Unauthorized'}

    def test_post_no_file(self):
        response = self.client.post('/v1/image/', json={}, headers={'X-API-KEY': 'TEST_API_KEY'})
        assert response.status_code == 400
        assert response.json == {'status': 'error', 'error': 'No file'}

    @pytest.mark.parametrize('filename', [
        'filename',
        None,
    ])
    def test_post_ok(self, filename):
        data = dict()
        data['base64'] = base64.b64encode(b'abcdef').decode()
        if filename:
            data['file_name'] = filename
        expected_filename = (filename + '-' if filename else '') + 'aaakXu8ab9'
        response = self.client.post(
            '/v1/image/',
            headers={'X-API-KEY': 'TEST_API_KEY'},
            json=data,
        )
        assert response.status_code == 200
        assert response.json == {
            'status': 'ok',
            'uuid': 'test_client/{}'.format(expected_filename),
        }
        assert self.env.image_storage_mock.call_count == 1
        assert self.env.image_storage_mock.return_value.save_image.call_count == 1
        save_image_call_kwargs = self.env.image_storage_mock.return_value.save_image.call_args.kwargs
        assert save_image_call_kwargs['uuid'] == ['test_client', expected_filename]
        assert save_image_call_kwargs['file_content'] == b'abcdef'
        assert json.loads(save_image_call_kwargs['data']) == dict(
            mimetype='image/jpeg',
        )

    def test_get_ok(self):
        self.env.image_storage_mock.return_value.uuid_exists.return_value = True
        self.env.image_storage_mock.return_value.read_file.return_value = io.BytesIO(b'abcdef')
        self.env.image_storage_mock.return_value.read_data.return_value = '{"mimetype": "image/jpeg"}'
        response = self.client.get('/v1/image/some_uuid')
        assert response.status_code == 200
        assert response.content_type == 'image/jpeg'
        assert response.data == b'abcdef'
        assert self.env.image_storage_mock.return_value.read_file.call_args.args[0] == ['some_uuid']

    def test_get_ok_with_client_id(self):
        self.env.image_storage_mock.return_value.uuid_exists.return_value = True
        self.env.image_storage_mock.return_value.read_file.return_value = io.BytesIO(b'abcdef')
        self.env.image_storage_mock.return_value.read_data.return_value = '{"mimetype": "image/jpeg"}'
        response = self.client.get('/v1/image/some_client_id/some_uuid')
        assert response.status_code == 200
        assert response.content_type == 'image/jpeg'
        assert response.data == b'abcdef'
        assert self.env.image_storage_mock.return_value.read_file.call_args.args[0] == ['some_client_id', 'some_uuid']

    def test_get_unknown_uuid(self):
        response = self.client.get('/v1/image/some_uuid')
        assert response.status_code == 404
