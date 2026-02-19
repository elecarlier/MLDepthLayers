# layout_utils.py

def compute_lens_width(hdpi, lpi):
    """
    Calcule la largeur d'une lentille en pixels.

    Paramètres:
        hdpi (int)
        lpi (float)

    Retour:
        float
    """
    return hdpi / lpi


def compute_max_copies(mire_size, image_size, lens_width):
    """
    Calcule le nombre maximal de copies horizontales et verticales.

    Paramètres:
        mire_size (tuple): (width, height)
        image_size (tuple): (width, height)
        lens_width (float)

    Retour:
        (max_h, max_v)
    """
    a1, b1 = mire_size
    a2, b2 = image_size

    max_h = int(a1 / (a2 + int(lens_width) + 1))
    max_v = int(b1 / b2)

    return max_h, max_v
