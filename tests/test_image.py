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

    @pytest.mark.parametrize(
        ("width", "height", "expected_size"),
        [
            (100, 100, (100, 50)),
            (100, None, (100, 50)),
            (None, 25, (50, 25)),
        ],
    )
    def test_resized_to_fit(self, width: int | None, height: int | None, expected_size: tuple[int, int]):
        pil_image = Image.new(mode="RGB", size=(200, 100))
        img_stream = io.BytesIO()
        pil_image.save(img_stream, format="jpeg")

        result = app.image.Image(data=img_stream.getvalue()).resized_to_fit(width=width, height=height)

        assert Image.open(io.BytesIO(result.data)).size == expected_size
        assert result.mimetype == "image/jpeg"

    def test_resized_to_fit_does_not_upscale(self):
        img_stream = io.BytesIO()
        self.pil_image.save(img_stream, format="jpeg")
        image = app.image.Image(data=img_stream.getvalue())

        result = image.resized_to_fit(width=100, height=100)

        assert result is image
