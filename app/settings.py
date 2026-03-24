# -*- coding: utf-8 -*-
from enum import Enum
from functools import cache
from typing import Any, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientInfo(BaseModel):
    id: str
    api_key: str


class StorageConfigS3(BaseModel):
    url: Optional[str] = None
    access_key: str = ""
    secret_key: str = ""
    bucket: str = ""


class StorageConfigDisk(BaseModel):
    path: str = ""


class StorageType(str, Enum):
    S3 = "s3"
    DISK = "disk"


class StorageConfig(BaseModel):
    type: StorageType = StorageType.S3
    s3: StorageConfigS3 = StorageConfigS3()
    disk: StorageConfigDisk = StorageConfigDisk()


class SentryConfig(BaseModel):
    dsn: str = ""


class Settings(BaseSettings):
    environment: str = "debug"
    version: str = "0.2.0"

    model_config = SettingsConfigDict(env_nested_delimiter="__")

    clients_info: dict[str, ClientInfo] = {}

    storage: StorageConfig = StorageConfig()

    sentry: SentryConfig = SentryConfig()


@cache
def get_settings() -> Settings:
    return Settings()


class LazySettings:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_settings(), name)


settings: Settings = LazySettings()  # type: ignore[assignment]
