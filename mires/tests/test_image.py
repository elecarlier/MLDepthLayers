import pytest
from PIL import Image

from mires.images_utils import trim_image, add_border

def test_trim_image():
    img = Image.new("RGB", (200, 200), color="white")

    trimmed = trim_image(img, trim_mm=10, hdpi=254, vdpi=254)
    # 254 dpi → 10 mm = 100 pixels environ

    assert trimmed.size[0] < img.size[0]
    assert trimmed.size[1] < img.size[1]


def test_add_border():
    img = Image.new("RGB", (100, 100), color="white")

    bordered = add_border(img, border_mm=10, hdpi=254, vdpi=254)

    assert bordered.size[0] > img.size[0]
    assert bordered.size[1] > img.size[1]
