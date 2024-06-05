# -*- coding: utf-8 -*-
import io
import os

import pytest
from PIL import Image

from app import storage_manager
from app.settings import S3Config, Settings


class TestStorageManager:
    @pytest.fixture(autouse=True)
    def _setup(self, upload_folder, monkeypatch):
        monkeypatch.setattr(storage_manager, "settings", Settings(upload_folder=upload_folder))
        self.upload_folder = upload_folder
        self.manager = storage_manager.StorageManager()

        self.image = Image.new(mode="RGB", size=(3, 3))
        img_stream = io.BytesIO()
        self.image.save(img_stream, format="jpeg")
        self.image_byte_array = img_stream.getvalue()

    def check_save(self, uuid):
        folder = os.path.join(self.upload_folder, uuid)
        file_path = os.path.join(folder, "file")

        assert os.path.isdir(folder)
        assert os.path.isfile(file_path)
        with open(file_path, "rb") as file:
            assert file.read() == self.image_byte_array

    def test_save_image_ok(self):
        self.manager.save_image(["some_uuid"], self.image_byte_array)
        self.check_save("some_uuid")

    @pytest.mark.parametrize("exists", [True, False])
    def test_exists(self, exists):
        if exists:
            os.makedirs(os.path.join(self.upload_folder, "some_uuid"))
        assert self.manager.uuid_exists(["some_uuid"]) == exists

    def test_get_image(self):
        os.makedirs(os.path.join(self.upload_folder, "some_uuid"))
        with open(os.path.join(self.upload_folder, "some_uuid", "file"), "wb") as f:
            f.write(self.image_byte_array)
        result_image = self.manager.get_image(["some_uuid"])
        assert result_image.data == self.image_byte_array
        assert result_image.mimetype == "image/jpeg"

    def test_path_for_uuid_with_sep(self):
        path = self.manager.path_for_uuid(["foo", "bar"])
        assert path == os.path.join(self.upload_folder, "foo", "bar")


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
