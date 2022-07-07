# -*- coding: utf-8 -*-
import os
from typing import BinaryIO

from . import settings


class StorageManager(object):
    def path_for_uuid(self, uuid: str) -> str:
        uuid = uuid.split(os.sep)
        return os.path.join(settings.UPLOAD_FOLDER, *uuid)

    def uuid_exists(self, uuid: str) -> bool:
        return os.path.exists(self.path_for_uuid(uuid))

    def save_image(self, uuid: str, file_content: bytes, data: str = None) -> None:
        folder = self.path_for_uuid(uuid)
        os.makedirs(folder)
        with open(os.path.join(folder, 'file'), 'wb') as f:
            f.write(file_content)
        if data:
            with open(os.path.join(folder, 'data'), 'w') as f:
                f.write(data)

    def read_data(self, uuid: str) -> str:
        with open(os.path.join(self.path_for_uuid(uuid), 'data'), 'r') as f:
            return f.read()

    def read_file(self, uuid: str) -> BinaryIO:
        return open(os.path.join(self.path_for_uuid(uuid), 'file'), 'rb')
