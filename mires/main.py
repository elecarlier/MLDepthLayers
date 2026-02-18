#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
from cli import parse_args
from models import PrintSettings, PrintContext
from dpi import resolve_dpi
from images_utils import trim_image, add_border
from layout import compute_max_copies


def run(args):
    settings = PrintSettings(
        lpi=args.LPI,
        user_hdpi=args.HDPI,
        user_vdpi=args.VDPI,
        trim_mm=args.trim,
        border_mm=args.border,
        tile=args.tile,
        makeshift=args.makeshift,
        cols=args.cols,
        rows=args.rows
    )

    # Charger la mire et l'image
    Image.MAX_IMAGE_PIXELS = None  # éviter warning grandes images ancienne valeur 2052314995
    mire = Image.open(args.mire)
    img2 = Image.open(args.image)

    context = PrintContext(settings, mire, img2)

    print("=== Settings ===")
    print(settings)
    print("=== Context ===")
    print(context)

    # Appliquer trim et border
    if settings.trim_mm > 0:
        img2 = trim_image(img2, settings.trim_mm, context)
    if settings.border_mm > 0:
        img2 = add_border(img2, settings.border_mm, context)

    # Calcul du nombre maximal de copies
    max_h, max_v = compute_max_copies((context.mire_width, context.mire_height),
                                      (context.image_width, context.image_height),
                                      context)
    print(f"Max copies HxV: {max_h} x {max_v}")

    # Fermer images
    mire.close()
    img2.close()


def main():
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()