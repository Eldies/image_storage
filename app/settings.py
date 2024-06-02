# -*- coding: utf-8 -*-
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientInfo(BaseModel):
    id: str
    api_key: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    upload_folder: str = ""
    clients_info: dict[str, ClientInfo] = {}


_settings = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
