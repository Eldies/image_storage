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

    def resized_to_fit(self, width: int | None = None, height: int | None = None) -> "Image":
        if width is None and height is None:
            return self

        pil_image = PIL.Image.open(io.BytesIO(self.data))
        original_width, original_height = pil_image.size
        target_width = width or original_width
        target_height = height or original_height
        if target_width >= original_width and target_height >= original_height:
            return self

        pil_image.thumbnail(
            (target_width, target_height),
            resample=PIL.Image.Resampling.LANCZOS,
        )

        img_stream = io.BytesIO()
        pil_image.save(img_stream, format=self.format)
        return Image(data=img_stream.getvalue())
