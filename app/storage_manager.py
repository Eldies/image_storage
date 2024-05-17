# -*- coding: utf-8 -*-
import json
import os
from typing import BinaryIO

from . import settings


class StorageManagerException(Exception):
    pass


class StorageManager(object):
    def path_for_uuid(self, uuid: list[str]) -> str:
        return os.path.join(settings.UPLOAD_FOLDER, *uuid)

    def uuid_exists(self, uuid: list[str]) -> bool:
        return os.path.exists(self.path_for_uuid(uuid))

    def save_image(self, uuid: list[str], file_content: bytes, data: str = None) -> None:
        folder = self.path_for_uuid(uuid)
        os.makedirs(folder)
        with open(os.path.join(folder, 'file'), 'wb') as f:
            f.write(file_content)
        if data:
            with open(os.path.join(folder, 'data'), 'w') as f:
                f.write(data)

    def _read_data(self, uuid: list[str]) -> str:
        with open(os.path.join(self.path_for_uuid(uuid), 'data'), 'r') as f:
            return f.read()

    def _read_file(self, uuid: list[str]) -> bytes:
        with open(os.path.join(self.path_for_uuid(uuid), 'file'), 'rb') as f:
            return f.read()

    def get_file(self, uuid: list[str]) -> tuple[bytes, dict]:
        if not self.uuid_exists(uuid):
            raise StorageManagerException('Not Found')
        return self._read_file(uuid), json.loads(self._read_data(uuid))


def get_storage_manager() -> StorageManager:
    return StorageManager()
