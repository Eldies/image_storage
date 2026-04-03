# -*- coding: utf-8 -*-
from enum import Enum
from functools import cache, cached_property
from typing import Any, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientConfig(BaseModel):
    api_key: str


class ClientInfo(ClientConfig):
    id: str


class ClientRegistry(BaseModel):
    by_id: dict[str, ClientInfo]
    by_api_key: dict[str, ClientInfo]


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

    raw_clients: dict[str, ClientConfig] = Field(default_factory=dict, alias="clients")

    storage: StorageConfig = StorageConfig()

    sentry: SentryConfig = SentryConfig()

    @cached_property
    def clients(self) -> ClientRegistry:
        by_id = {client_id: ClientInfo(id=client_id, **cfg.model_dump()) for client_id, cfg in self.raw_clients.items()}
        by_api_key = {client.api_key: client for client in by_id.values()}
        return ClientRegistry(by_id=by_id, by_api_key=by_api_key)


@cache
def get_settings() -> Settings:
    return Settings()


class LazySettings:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_settings(), name)


settings: Settings = LazySettings()  # type: ignore[assignment]
