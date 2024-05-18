# -*- coding: utf-8 -*-
import base64
import json
import os

import pytest
import pytest_asyncio


@pytest.fixture()
def generate_image_uuid_mock(monkeypatch):
    def mock_func(suggested_filename):
        return f'{suggested_filename or "aaa"}_generated'
    monkeypatch.setattr('app.views.generate_image_uuid', mock_func)


@pytest.mark.asyncio
class TestImageViewPost:
    @pytest_asyncio.fixture(autouse=True)
    async def _setup(self, client, generate_image_uuid_mock, upload_folder):
        self.client = client
        self.upload_folder = upload_folder

    async def test_no_api_key(self):
        response = await self.client.post('/v1/image/', json={})
        assert response.status_code == 401
        assert response.json() == {'status': 'error', 'error': 'Not authenticated'}

    async def test_wrong_api_key(self):
        response = await self.client.post('/v1/image/', headers={'X-API-KEY': 'random_string'}, json={})
        assert response.status_code == 401
        assert response.json() == {'status': 'error', 'error': 'Not authenticated'}

    async def test_no_file(self):
        response = await self.client.post('/v1/image/', json={}, headers={'X-API-KEY': 'TEST_API_KEY'})
        assert response.status_code == 400
        assert response.json() == {'status': 'error', 'error': 'No file'}

    @pytest.mark.parametrize('filename', [
        'filename',
        None,
    ])
    async def test_ok(self, filename):
        data = dict()
        data['base64'] = base64.b64encode(b'abcdef').decode()
        if filename:
            data['file_name'] = filename
        expected_filename = (filename if filename else 'aaa') + '_generated'
        response = await self.client.post(
            '/v1/image/',
            headers={'X-API-KEY': 'TEST_API_KEY'},
            json=data,
        )
        assert response.status_code == 200
        assert response.json() == {
            'status': 'ok',
            'uuid': 'test_client/{}'.format(expected_filename),
        }
        assert os.path.isdir(os.path.join(self.upload_folder, 'test_client', expected_filename))
        with open(os.path.join(self.upload_folder, 'test_client', expected_filename, 'file'), 'rb') as file:
            assert file.read() == b'abcdef'
        with open(os.path.join(self.upload_folder, 'test_client', expected_filename, 'data'), 'r') as file:
            assert json.loads(file.read()) == dict(
                mimetype='image/jpeg',
            )


@pytest.mark.asyncio
class TestImageViewGet:
    @pytest_asyncio.fixture(autouse=True)
    def _setup(self, client, upload_folder):
        self.client = client
        os.makedirs(os.path.join(upload_folder, 'some_client_id', 'some_uuid'))
        with open(os.path.join(upload_folder, 'some_client_id', 'some_uuid', 'file'), 'wb') as f:
            f.write(b'abcdef')
        with open(os.path.join(upload_folder, 'some_client_id', 'some_uuid', 'data'), 'w') as f:
            f.write(json.dumps(dict(mimetype='image/jpeg')))

    async def test_ok(self):
        response = await self.client.get('/v1/image/some_client_id/some_uuid')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'image/jpeg'
        assert response.content == b'abcdef'

    async def test_no_client_id(self):
        response = await self.client.get('/v1/image/some_uuid')
        assert response.status_code == 404
        assert response.headers['Content-Type'] == 'application/json'
        assert response.json() == dict(
            status='error',
            error='Not Found',
        )

    async def test_unknown_uuid(self):
        response = await self.client.get('/v1/image/some_client/some_other_uuid')
        assert response.status_code == 404
        assert response.headers['Content-Type'] == 'application/json'
        assert response.json() == dict(
            status='error',
            error='Not Found',
        )
