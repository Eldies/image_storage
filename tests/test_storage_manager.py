# -*- coding: utf-8 -*-
import io

import pytest
from PIL import Image

from app import storage_manager
from app.settings import S3Config, Settings


class TestS3StorageManager:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_s3_bucket, monkeypatch):
        monkeypatch.setattr(storage_manager, "settings", Settings(s3=S3Config(bucket=mock_s3_bucket.name)))
        self.bucket = mock_s3_bucket
        self.manager = storage_manager.S3StorageManager()

        self.image = Image.new(mode="RGB", size=(3, 3))
        img_stream = io.BytesIO()
        self.image.save(img_stream, format="jpeg")
        self.image_byte_array = img_stream.getvalue()

    def test_save_image_ok(self):
        self.manager.save_image(["client", "some_uuid"], self.image_byte_array)
        created_object = self.bucket.Object("client/some_uuid").get()
        assert created_object["Body"].read() == self.image_byte_array
        assert created_object["ContentType"] == "image/jpeg"

    def test_get_image(self):
        self.bucket.Object("some_uuid").put(Body=self.image_byte_array)
        result_image = self.manager.get_image(["some_uuid"])
        assert result_image.data == self.image_byte_array
        assert result_image.mimetype == "image/jpeg"

    def test_uuid_exists(self):
        self.bucket.Object("some_uuid").put(Body=self.image_byte_array)
        assert self.manager.uuid_exists(["some_uuid"]) is True
        assert self.manager.uuid_exists(["some_other_uuid"]) is False

    def test_list_uuids(self):
        assert self.manager.list_uuids() == []
        self.bucket.Object("some_uuid").put(Body=self.image_byte_array)
        assert self.manager.list_uuids() == [["some_uuid"]]
        self.bucket.Object("some/other/uuid").put(Body=self.image_byte_array)
        assert sorted(self.manager.list_uuids()) == [["some", "other", "uuid"], ["some_uuid"]]

    def test_get_image_unknown_key(self):
        with pytest.raises(storage_manager.StorageManagerException):
            self.manager.get_image(["some_uuid"])
