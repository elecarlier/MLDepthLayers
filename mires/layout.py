


def compute_max_copies(mire_size, image_size, context):
    a1, b1 = mire_size
    a2, b2 = image_size

    lens = int(context.lens_width_px)

    max_h = int(a1 / (a2 + lens + 1))
    max_v = int(b1 / b2)

    return max_h, max_v
