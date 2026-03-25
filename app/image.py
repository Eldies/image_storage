# -*- coding: utf-8 -*-
import io
from dataclasses import dataclass

import PIL
import PIL.Image

from app.exceptions import UnprocessableImageError


@dataclass
class Image:
    data: bytes
    format: str = ""

    def __post_init__(self) -> None:
        try:
            pil_image = PIL.Image.open(io.BytesIO(self.data))
            if not pil_image.format:
                raise UnprocessableImageError()
            self.format = pil_image.format
        except PIL.UnidentifiedImageError:
            raise UnprocessableImageError()

    @property
    def mimetype(self) -> str:
        return PIL.Image.MIME[self.format]
