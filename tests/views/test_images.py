# -*- coding: utf-8 -*-
import base64
import io

import pytest
from PIL import Image


@pytest.fixture()
def generate_image_uuid_mock(monkeypatch):
    def mock_func(suggested_filename):
        return f'{suggested_filename or "aaa"}_generated'

    monkeypatch.setattr("app.views.generate_image_uuid", mock_func)


@pytest.mark.asyncio
class TestImageViewPost:
    @pytest.fixture(autouse=True)
    def _setup(self, client, generate_image_uuid_mock, mock_s3_bucket):
        self.client = client
        self.bucket = mock_s3_bucket

        self.image = Image.new(mode="RGB", size=(3, 3))
        img_stream = io.BytesIO()
        self.image.save(img_stream, format="jpeg")
        self.image_byte_array = img_stream.getvalue()

    async def test_no_api_key(self):
        response = await self.client.post("/v1/image/", json={})
        assert response.status_code == 403
        assert response.json() == {"status": "error", "error": "Not authenticated"}

    async def test_wrong_api_key(self):
        response = await self.client.post("/v1/image/", headers={"X-API-KEY": "random_string"}, json={})
        assert response.status_code == 401
        assert response.json() == {"status": "error", "error": "Not authenticated"}

    async def test_no_file(self):
        response = await self.client.post("/v1/image/", json={}, headers={"X-API-KEY": "TEST_API_KEY"})
        assert response.status_code == 400
        assert response.json() == {"status": "error", "error": "No file"}

    @pytest.mark.parametrize(
        "filename",
        [
            "filename",
            None,
        ],
    )
    async def test_ok(self, filename):
        data = dict()
        data["base64"] = base64.b64encode(self.image_byte_array).decode()
        if filename:
            data["file_name"] = filename
        expected_filename = (filename if filename else "aaa") + "_generated"
        response = await self.client.post(
            "/v1/image/",
            headers={"X-API-KEY": "TEST_API_KEY"},
            json=data,
        )
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "uuid": "test_client/{}".format(expected_filename),
        }
        assert self.bucket.Object(f"test_client/{expected_filename}").get()["Body"].read() == self.image_byte_array


@pytest.mark.asyncio
class TestImageViewGet:
    @pytest.fixture(autouse=True)
    def _setup(self, client, mock_s3_bucket):
        self.client = client
        self.bucket = mock_s3_bucket

        image = Image.new(mode="RGB", size=(3, 3))
        img_stream = io.BytesIO()
        image.save(img_stream, format="jpeg")
        self.image_byte_array = img_stream.getvalue()
        self.bucket.Object("some_client_id/some_uuid").put(Body=self.image_byte_array)

    async def test_ok(self):
        response = await self.client.get("/v1/image/some_client_id/some_uuid")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "image/jpeg"
        assert response.content == self.image_byte_array

    async def test_no_client_id(self):
        response = await self.client.get("/v1/image/some_uuid")
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"
        assert response.json() == dict(
            status="error",
            error="Not Found",
        )

    async def test_unknown_uuid(self):
        response = await self.client.get("/v1/image/some_client/some_other_uuid")
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"
        assert response.json() == dict(
            status="error",
            error="Not Found",
        )
