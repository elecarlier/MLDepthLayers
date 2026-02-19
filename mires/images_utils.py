# image_utils.py

from PIL import Image, ImageOps
from pathlib import Path

def trim_image(img, context):
    """Trim l'image selon le context"""

    # On utilise les pixels déjà calculés
    px_h = context.trim_px_h
    px_v = context.trim_px_v

    print("Trimming", px_h,px_v,"pixels")

    w, h = img.size #valeurs avant le trim

    #on retur px_h à gauche et droite et px_v en haut et en bas
    return img.crop((px_h, px_v, w - px_h, h - px_v))


def add_border(img, context):
    """Ajoute un bord noir autour de l'image."""

    # On utilise les pixels déjà calculés dans context
    px_h = context.border_px_h
    px_v = context.border_px_v

    # Bord gauche/droite = px_h, haut/bas = px_v
    return ImageOps.expand(img, border=(px_h, px_v, px_h, px_v), fill=(0, 0, 0))

