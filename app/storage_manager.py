# -*- coding: utf-8 -*-
import json
import os
from aiofile import async_open

from . import settings


class StorageManagerException(Exception):
    pass


class StorageManager(object):
    def path_for_uuid(self, uuid: list[str]) -> str:
        return os.path.join(settings.UPLOAD_FOLDER, *uuid)

    def uuid_exists(self, uuid: list[str]) -> bool:
        return os.path.exists(self.path_for_uuid(uuid))

    async def save_image(self, uuid: list[str], file_content: bytes, data: str = None) -> None:
        folder = self.path_for_uuid(uuid)
        os.makedirs(folder)
        async with async_open(os.path.join(folder, 'file'), 'wb') as f:
            await f.write(file_content)
        if data:
            async with async_open(os.path.join(folder, 'data'), 'w') as f:
                await f.write(data)

    async def _read_data(self, uuid: list[str]) -> dict:
        path = os.path.join(self.path_for_uuid(uuid), 'data')
        if not os.path.exists(path):
            return {}
        async with async_open(path, 'r') as f:
            return json.loads(await f.read())

    async def _read_file(self, uuid: list[str]) -> bytes:
        async with async_open(os.path.join(self.path_for_uuid(uuid), 'file'), 'rb') as f:
            return await f.read()

    async def get_file(self, uuid: list[str]) -> tuple[bytes, dict]:
        if not self.uuid_exists(uuid):
            raise StorageManagerException('Not Found')
        return await self._read_file(uuid), await self._read_data(uuid)


def get_storage_manager() -> StorageManager:
    return StorageManager()
