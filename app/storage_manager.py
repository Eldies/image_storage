# -*- coding: utf-8 -*-
import logging
from functools import cache

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_s3.service_resource import Object

from .image import Image
from .settings import settings

logger = logging.getLogger("image-storage")


class StorageManagerException(Exception):
    pass


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

    def save_image(self, uuid: list[str], image: Image) -> None:
        self.object_for_uuid(uuid).put(
            Body=image.data,
            ContentType=image.mimetype,
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
            return Image(
                data=self.object_for_uuid(uuid).get()["Body"].read(),
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise StorageManagerException("Not Found")
            raise


@cache
def get_storage_manager() -> S3StorageManager:
    return S3StorageManager()
