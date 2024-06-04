# -*- coding: utf-8 -*-
import io
import os
from dataclasses import dataclass

from PIL import Image as PILImage

from .settings import settings


class StorageManagerException(Exception):
    pass


@dataclass
class Image:
    data: bytes
    mimetype: str


class StorageManager(object):
    def path_for_uuid(self, uuid: list[str]) -> str:
        return os.path.join(settings.upload_folder, *uuid)

    def uuid_exists(self, uuid: list[str]) -> bool:
        return os.path.exists(self.path_for_uuid(uuid))

    def save_image(self, uuid: list[str], file_content: bytes) -> None:
        folder = self.path_for_uuid(uuid)
        os.makedirs(folder)
        with open(os.path.join(folder, "file"), "wb") as f:
            f.write(file_content)

    def get_image(self, uuid: list[str]) -> Image:
        if not self.uuid_exists(uuid):
            raise StorageManagerException("Not Found")
        filename = os.path.join(self.path_for_uuid(uuid), "file")
        with open(filename, "rb") as f:
            data = f.read()
        pil_image = PILImage.open(io.BytesIO(data))
        assert pil_image.format is not None
        return Image(
            data=data,
            mimetype=PILImage.MIME[pil_image.format],
        )


def get_storage_manager() -> StorageManager:
    return StorageManager()
