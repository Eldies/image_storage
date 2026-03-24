import io
from dataclasses import dataclass
from functools import cached_property

import PIL
import PIL.Image


class ImageException(Exception):
    pass


@dataclass
class Image:
    data: bytes

    @cached_property
    def format(self) -> str:
        try:
            pil_image = PIL.Image.open(io.BytesIO(self.data))
            assert pil_image.format is not None
            return pil_image.format
        except PIL.UnidentifiedImageError:
            raise ImageException("Cannot identify image file")

    @property
    def mimetype(self) -> str:
        return PIL.Image.MIME[self.format]
