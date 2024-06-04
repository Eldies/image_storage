# -*- coding: utf-8 -*-
import io
import logging
import os
from dataclasses import dataclass
from functools import cache

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_s3.service_resource import Object
from PIL import Image as PILImage

from .settings import settings

logger = logging.getLogger("image-storage")


class StorageManagerException(Exception):
    pass


@dataclass
class Image:
    data: bytes
    mimetype: str


def get_content_type_for_data(data: bytes) -> str:
    pil_image = PILImage.open(io.BytesIO(data))
    assert pil_image.format is not None
    return PILImage.MIME[pil_image.format]


class StorageManager(object):
    def path_for_uuid(self, uuid: list[str]) -> str:
        return os.path.join(settings.upload_folder, *uuid)

    def uuid_exists(self, uuid: list[str]) -> bool:
        return os.path.exists(self.path_for_uuid(uuid))

    def save_image(self, uuid: list[str], file_content: bytes) -> None:
        folder = self.path_for_uuid(uuid)
        os.makedirs(folder)
        with open(os.path.join(folder, "file"), "wb") as f:
            f.write(file_content)

    def get_image(self, uuid: list[str]) -> Image:
        if not self.uuid_exists(uuid):
            raise StorageManagerException("Not Found")
        filename = os.path.join(self.path_for_uuid(uuid), "file")
        with open(filename, "rb") as f:
            data = f.read()
        pil_image = PILImage.open(io.BytesIO(data))
        assert pil_image.format is not None
        return Image(
            data=data,
            mimetype=PILImage.MIME[pil_image.format],
        )


class S3StorageManager(object):
    def __init__(self) -> None:
        s3_resource = boto3.resource(
            "s3",
            endpoint_url=settings.s3.url,
            aws_access_key_id=settings.s3.access_key,
            aws_secret_access_key=settings.s3.secret_key,
            aws_session_token=None,
        )
        self.bucket = s3_resource.Bucket(settings.s3.bucket)

    def object_for_uuid(self, uuid: list[str]) -> Object:
        return self.bucket.Object("/".join(uuid))

    def save_image(self, uuid: list[str], file_content: bytes) -> None:
        self.object_for_uuid(uuid).put(
            Body=file_content,
            ContentType=get_content_type_for_data(file_content),
        )

    def list_uuids(self) -> list[list[str]]:
        return [object_summary.key.split("/") for object_summary in self.bucket.objects.all()]

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
            logger.debug("logger - get image start")
            data = self.object_for_uuid(uuid).get()["Body"].read()
            mimetype = get_content_type_for_data(data)
            logger.debug("logger - get image end")
            return Image(
                data=data,
                mimetype=mimetype,
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return StorageManager().get_image(uuid)
                # raise StorageManagerException("Not Found")
            raise


@cache
def get_storage_manager() -> S3StorageManager:
    return S3StorageManager()
