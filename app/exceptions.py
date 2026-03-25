# -*- coding: utf-8 -*-
from __future__ import annotations


class ImageStorageOutException(Exception):
    status_code: int
    detail: str


class UnprocessableImageError(ImageStorageOutException):
    status_code = 422
    detail = "Cannot process image file"


class ImageNotFoundError(ImageStorageOutException):
    status_code = 404
    detail = "Image does not exist"
