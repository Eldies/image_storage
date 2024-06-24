import io

import pytest
from PIL import Image

import app.image


class TestImage:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.pil_image = Image.new(mode="RGB", size=(3, 3))

    @pytest.mark.parametrize(
        "image_format",
        [
            "jpeg",
            "png",
            "bmp",
        ],
    )
    def test_mimetype(self, image_format: str):
        img_stream = io.BytesIO()
        self.pil_image.save(img_stream, format=image_format)
        image = app.image.Image(data=img_stream.getvalue())
        assert image.mimetype == f"image/{image_format}"
