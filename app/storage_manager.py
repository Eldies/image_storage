# -*- coding: utf-8 -*-
import json
import os

from .settings import get_settings


class StorageManagerException(Exception):
    pass


class StorageManager(object):
    def path_for_uuid(self, uuid: list[str]) -> str:
        return os.path.join(get_settings().upload_folder, *uuid)

    def uuid_exists(self, uuid: list[str]) -> bool:
        return os.path.exists(self.path_for_uuid(uuid))

    def save_image(self, uuid: list[str], file_content: bytes, data: str | None = None) -> None:
        folder = self.path_for_uuid(uuid)
        os.makedirs(folder)
        with open(os.path.join(folder, "file"), "wb") as f:
            f.write(file_content)
        if data:
            with open(os.path.join(folder, "data"), "w") as f:
                f.write(data)

    def _read_data(self, uuid: list[str]) -> dict:
        path = os.path.join(self.path_for_uuid(uuid), "data")
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.loads(f.read())

    def _read_file(self, uuid: list[str]) -> bytes:
        with open(os.path.join(self.path_for_uuid(uuid), "file"), "rb") as f:
            return f.read()

    def get_file(self, uuid: list[str]) -> tuple[bytes, dict]:
        if not self.uuid_exists(uuid):
            raise StorageManagerException("Not Found")
        return self._read_file(uuid), self._read_data(uuid)


def get_storage_manager() -> StorageManager:
    return StorageManager()
