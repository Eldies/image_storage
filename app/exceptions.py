# -*- coding: utf-8 -*-
from __future__ import annotations


class ImageStorageException(Exception):
    status_code: int
    detail: str


class UnprocessableImageException(ImageStorageException):
    status_code = 422
    detail = "Cannot process image file"


class ImageNotFoundError(ImageStorageException):
    status_code = 404
    detail = "Image does not exist"
