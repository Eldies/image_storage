import io
from dataclasses import dataclass
from functools import cached_property

from PIL import Image as PILImage


@dataclass
class Image:
    data: bytes

    @cached_property
    def mimetype(self) -> str:
        pil_image = PILImage.open(io.BytesIO(self.data))
        assert pil_image.format is not None
        return PILImage.MIME[pil_image.format]
