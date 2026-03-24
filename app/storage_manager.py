# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import boto3
from botocore.exceptions import ClientError

from .image import Image
from .settings import StorageType, settings

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import Object  # pragma: no cover

logger = logging.getLogger("image-storage")


class StorageManagerException(Exception):
    pass


class StorageManagerInterface:
    def save_image(self, uuid: list[str], image: Image) -> None:
        raise NotImplementedError

    def uuid_exists(self, uuid: list[str]) -> bool:
        raise NotImplementedError

    def get_image(self, uuid: list[str]) -> Image:
        raise NotImplementedError


class S3StorageManager(StorageManagerInterface):
    def __init__(self) -> None:
        s3_resource = boto3.resource(
            "s3",
            endpoint_url=settings.storage.s3.url,
            aws_access_key_id=settings.storage.s3.access_key,
            aws_secret_access_key=settings.storage.s3.secret_key,
            aws_session_token=None,
        )
        self.bucket = s3_resource.Bucket(settings.storage.s3.bucket)

    def object_for_uuid(self, uuid: list[str]) -> Object:
        return self.bucket.Object("/".join(uuid))

    def save_image(self, uuid: list[str], image: Image) -> None:
        self.object_for_uuid(uuid).put(
            Body=image.data,
            ContentType=image.mimetype,
        )

    def uuid_exists(self, uuid: list[str]) -> bool:
        try:
            self.object_for_uuid(uuid).load()
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def get_image(self, uuid: list[str]) -> Image:
        try:
            return Image(
                data=self.object_for_uuid(uuid).get()["Body"].read(),
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise StorageManagerException("Not Found")
            raise


class DiskStorageManager(StorageManagerInterface):
    @staticmethod
    def image_path_for_uuid(uuid: list[str]) -> Path:
        return Path(settings.storage.disk.path, *uuid, "file")

    def save_image(self, uuid: list[str], image: Image) -> None:
        path = self.image_path_for_uuid(uuid)
        path.parent.mkdir(parents=True, exist_ok=False)
        with open(path, "wb") as f:
            f.write(image.data)

    def uuid_exists(self, uuid: list[str]) -> bool:
        return self.image_path_for_uuid(uuid).exists()

    def get_image(self, uuid: list[str]) -> Image:
        path = self.image_path_for_uuid(uuid)
        if not path.exists():
            raise StorageManagerException("Not Found")
        with open(path, "rb") as f:
            return Image(data=f.read())


@cache
def get_storage_manager() -> S3StorageManager:
    if settings.storage.type == StorageType.S3:
        return S3StorageManager()
    raise NotImplementedError
