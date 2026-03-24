# -*- coding: utf-8 -*-
import io
import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image as PILImage

from app import storage_manager
from app.image import Image
from app.settings import StorageType
from app.storage_manager import StorageManagerInterface


class TestGetStorageManager:
    EXPECTED_CLASS: dict[StorageType, type[StorageManagerInterface]] = {
        StorageType.S3: storage_manager.S3StorageManager,
        StorageType.DISK: storage_manager.DiskStorageManager,
    }

    def test_expected_mapping_is_exhaustive(self) -> None:
        assert set(self.EXPECTED_CLASS) == set(StorageType)

    @pytest.mark.parametrize(
        ("storage_type", "expected_class"),
        EXPECTED_CLASS.items(),
    )
    def test_get_prefix(self, mock_settings, storage_type: StorageType, expected_class: type[StorageManagerInterface]):
        storage_manager.get_storage_manager.cache_clear()
        mock_settings.storage.type = storage_type
        assert isinstance(storage_manager.get_storage_manager(), expected_class)


class TestS3StorageManager:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_s3_bucket, mock_settings):
        mock_settings.storage.type = StorageType.S3
        mock_settings.storage.s3.bucket = mock_s3_bucket.name
        self.bucket = mock_s3_bucket
        self.manager = storage_manager.S3StorageManager()

        self.pil_image = PILImage.new(mode="RGB", size=(3, 3))
        img_stream = io.BytesIO()
        self.pil_image.save(img_stream, format="jpeg")
        self.image_byte_array = img_stream.getvalue()

    def test_save_image_ok(self):
        self.manager.save_image(["client", "some_uuid"], Image(data=self.image_byte_array))
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

    def test_get_image_unknown_key(self):
        with pytest.raises(storage_manager.StorageManagerException):
            self.manager.get_image(["some_uuid"])


class TestDiskStorageManager:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_settings):
        self.pil_image = PILImage.new(mode="RGB", size=(3, 3))
        img_stream = io.BytesIO()
        self.pil_image.save(img_stream, format="jpeg")
        self.image_byte_array = img_stream.getvalue()

        mock_settings.storage.type = StorageType.DISK
        with tempfile.TemporaryDirectory() as folder:
            mock_settings.storage.disk.path = self.folder = folder
            self.manager = storage_manager.DiskStorageManager()
            yield

    def _create_image_for_uuid(self, uuid):
        folder = Path(self.folder, *uuid)
        folder.mkdir(parents=True, exist_ok=False)
        with open(folder / "file", "wb") as f:
            f.write(self.image_byte_array)

    def test_save_image_ok(self):
        self.manager.save_image(["client", "some_uuid"], Image(data=self.image_byte_array))
        with open(os.path.join(self.folder, "client", "some_uuid", "file"), "rb") as f:
            created_bytes = f.read()
        assert created_bytes == self.image_byte_array

    def test_get_image(self):
        uuid = ["client", "some_uuid"]
        self._create_image_for_uuid(uuid)
        result_image = self.manager.get_image(uuid)
        assert result_image.data == self.image_byte_array
        assert result_image.mimetype == "image/jpeg"

    def test_uuid_exists(self):
        self._create_image_for_uuid(["some_uuid"])
        assert self.manager.uuid_exists(["some_uuid"]) is True
        assert self.manager.uuid_exists(["some_other_uuid"]) is False

    def test_get_image_unknown_key(self):
        with pytest.raises(storage_manager.StorageManagerException):
            self.manager.get_image(["some_uuid"])
