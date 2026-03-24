import io
from dataclasses import dataclass
from functools import cached_property

from PIL import Image as PILImage


@dataclass
class Image:
    data: bytes

    @cached_property
    def format(self) -> str:
        pil_image = PILImage.open(io.BytesIO(self.data))
        assert pil_image.format is not None
        return pil_image.format

    def mimetype(self) -> str:
        return PILImage.MIME[self.format]
