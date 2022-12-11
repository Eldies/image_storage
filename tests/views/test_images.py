# -*- coding: utf-8 -*-
import base64
import json

import pytest
from werkzeug.exceptions import Unauthorized


@pytest.fixture()
def generate_image_uuid_mock(monkeypatch):
    def mock_func(suggested_filename):
        return f'{suggested_filename or "aaa"}_generated'
    monkeypatch.setattr('app.views.generate_image_uuid', mock_func)


class TestImageViewPost:
    @pytest.fixture(autouse=True)
    def _setup(self, client, generate_image_uuid_mock, fs):
        self.client = client
        self.fake_filesystem = fs

    def test_no_api_key(self):
        response = self.client.post('/v1/image/')
        assert response.status_code == 401
        assert response.json == {'status': 'error', 'error': Unauthorized.description}

    def test_wrong_api_key(self):
        response = self.client.post('/v1/image/', headers={'X-API-KEY': 'random_string'})
        assert response.status_code == 401
        assert response.json == {'status': 'error', 'error': Unauthorized.description}

    def test_no_file(self):
        response = self.client.post('/v1/image/', json={}, headers={'X-API-KEY': 'TEST_API_KEY'})
        assert response.status_code == 400
        assert response.json == {'status': 'error', 'error': 'No file'}

    @pytest.mark.parametrize('filename', [
        'filename',
        None,
    ])
    def test_ok(self, filename):
        data = dict()
        data['base64'] = base64.b64encode(b'abcdef').decode()
        if filename:
            data['file_name'] = filename
        expected_filename = (filename if filename else 'aaa') + '_generated'
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
        assert self.fake_filesystem.isdir(f'/test_upload_path/test_client/{expected_filename}')
        with open(f'/test_upload_path/test_client/{expected_filename}/file', 'rb') as file:
            assert file.read() == b'abcdef'
        with open(f'/test_upload_path/test_client/{expected_filename}/data', 'r') as file:
            assert json.loads(file.read()) == dict(
                mimetype='image/jpeg',
            )


class TestImageViewGet:
    @pytest.fixture(autouse=True)
    def _setup(self, client, fs):
        self.client = client
        self.fake_filesystem = fs
        self.fake_filesystem.create_file(
            '/test_upload_path/some_client_id/some_uuid/file',
            contents=b'abcdef',
        )
        self.fake_filesystem.create_file(
            '/test_upload_path/some_client_id/some_uuid/data',
            contents=json.dumps(dict(mimetype='image/jpeg')),
        )

    def test_ok(self):
        response = self.client.get('/v1/image/some_client_id/some_uuid')
        assert response.status_code == 200
        assert response.content_type == 'image/jpeg'
        assert response.data == b'abcdef'

    def test_no_client_id(self):
        response = self.client.get('/v1/image/some_uuid')
        assert response.status_code == 404
        assert response.content_type == 'application/json'
        assert response.json == dict(
            status='error',
            error='The requested URL was not found on the server.'
                  ' If you entered the URL manually please check your spelling and try again.',
        )

    def test_unknown_uuid(self):
        response = self.client.get('/v1/image/some_client/some_other_uuid')
        assert response.status_code == 404
        assert response.content_type == 'application/json'
        assert response.json == dict(
            status='error',
            error='Not Found',
        )
