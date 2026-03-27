# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Callable

import boto3
from botocore.exceptions import ClientError
from tenacity import retry, retry_if_exception_type

from .exceptions import ImageNotFoundError
from .image import Image
from .settings import StorageType, settings

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import Object  # pragma: no cover

logger = logging.getLogger("image-storage")


class ImageAlreadyExistsError(Exception):
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
        try:
            self.object_for_uuid(uuid).put(
                Body=image.data,
                ContentType=image.mimetype,
                IfNoneMatch="*",
            )
        except ClientError as e:
            if (
                e.response["Error"]["Code"] == "PreconditionFailed"
                and e.response["Error"]["Condition"] == "If-None-Match"  # type: ignore[typeddict-item]
            ):
                raise ImageAlreadyExistsError
            raise

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
                raise ImageNotFoundError()
            raise


class DiskStorageManager(StorageManagerInterface):
    @staticmethod
    def image_path_for_uuid(uuid: list[str]) -> Path:
        return Path(settings.storage.disk.path, *uuid, "file")

    def save_image(self, uuid: list[str], image: Image) -> None:
        path = self.image_path_for_uuid(uuid)
        try:
            path.parent.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            raise ImageAlreadyExistsError(f"Image with uuid {uuid} already exists")
        with open(path, "wb") as f:
            f.write(image.data)

    def uuid_exists(self, uuid: list[str]) -> bool:
        return self.image_path_for_uuid(uuid).exists()

    def get_image(self, uuid: list[str]) -> Image:
        path = self.image_path_for_uuid(uuid)
        if not path.exists():
            raise ImageNotFoundError()
        with open(path, "rb") as f:
            return Image(data=f.read())


@cache
def get_storage_manager() -> StorageManagerInterface:
    if settings.storage.type == StorageType.S3:
        return S3StorageManager()
    elif settings.storage.type == StorageType.DISK:
        return DiskStorageManager()
    raise Exception(f"Unknown storage type {settings.storage.type}")


@retry(retry=retry_if_exception_type(ImageAlreadyExistsError))
def save_image_retrying(uuid_generator: Callable[[], list[str]], image: Image) -> list[str]:
    uuid = uuid_generator()
    get_storage_manager().save_image(uuid=uuid, image=image)
    return uuid
