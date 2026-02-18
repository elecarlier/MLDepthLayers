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
    # if settings.trim_mm > 0 and settings.makeshift <= 0: 
        
    if settings.trim_mm > 0 and settings.makeshift <= 0:
        img2 = trim_image(img2, settings.trim_mm, context)

    
    context.image_size = img2.size #mise à jour 
    
    if settings.border_mm > 0 and settings.makeshift <= 0:
        img2 = add_border(img2, settings.border_mm, context)

    context.image_size = img2.size #mise à jour 

    # Fermer images
    mire.close()
    img2.close()

    print("=== Context ===")
    print(context)

    # Calcul du nombre maximal de copies
    copies_h, copies_v = compute_max_copies(context)
    print(f"Copies HxV: {copies_h} x {copies_v}")



def main():
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()