import pytest
from mires.layout_utils import compute_lens_width, compute_max_copies

def test_compute_lens_width():
    assert compute_lens_width(400, 40) == 10
    assert compute_lens_width(300, 50) == 6


def test_compute_max_copies_simple():
    mire_size = (1000, 500)
    image_size = (100, 100)
    lens_width = 10

    max_h, max_v = compute_max_copies(mire_size, image_size, lens_width)

    assert max_h == int(1000 / (100 + 10 + 1))
    assert max_v == int(500 / 100)
