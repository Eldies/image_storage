# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientInfo(BaseModel):
    id: str
    api_key: str


class S3Config(BaseModel):
    url: Optional[str] = None
    access_key: str = ""
    secret_key: str = ""
    bucket: str = ""


class SentryConfig(BaseModel):
    dsn: str = ""


class Settings(BaseSettings):
    environment: str = "debug"
    version: str = "0.2.0"

    model_config = SettingsConfigDict(env_nested_delimiter="__")

    clients_info: dict[str, ClientInfo] = {}

    s3: S3Config = S3Config()

    sentry: SentryConfig = SentryConfig()


settings = Settings()
