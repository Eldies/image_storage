# -*- coding: utf-8 -*-
import re

from pydantic import BaseModel, field_validator

FILE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9._/-]+$")


class PostImageRequest(BaseModel):
    file_name: str | None = None
    base64: bytes

    @field_validator("file_name")
    @classmethod
    def validate_file_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not FILE_NAME_PATTERN.fullmatch(value):
            raise ValueError("file_name may only contain letters, digits, '.', '-', '_', and '/'")
        if any(part in {"", ".", ".."} for part in value.split("/")):
            raise ValueError("file_name must not contain empty, '.', or '..' path segments")
        return value


class PostImageResponse(BaseModel):
    status: str = "ok"
    uuid: str


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
