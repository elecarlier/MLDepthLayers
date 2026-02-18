#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
from cli import parse_args
from models import PrintSettings, PrintContext
from dpi import resolve_dpi
from images_utils import trim_image, add_border
from layout import compute_max_copies, compute_actual_copies
from output import compute_output_filename

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
        rows=args.rows,
        hcopies=args.HCopies,
        vcopies=args.VCopies,
        hpos=args.HPos,
        vpos=args.VPos,
        test=args.test,
        shiftlist=args.shiftlist
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

    #ici si pas de mire de cadrage 

    # Appliquer trim et border
    # if settings.trim_mm > 0 and settings.makeshift <= 0: 

    if settings.trim_mm > 0:
        img2 = trim_image(img2, settings.trim_mm, context)

    
    context.image_size = img2.size #mise à jour 

    if settings.border_mm > 0:
        img2 = add_border(img2, settings.border_mm, context)

    context.image_size = img2.size #mise à jour 

    # Fermer images
    mire.close()
    img2.close()

    print("=== Context ===")
    print(context)

    # Calcul du nombre maximal de copies
    Max_copies_h, Max_copies_v = compute_max_copies(context)
    print(f"Max Copies HxV: {Max_copies_h} x {Max_copies_v}")


    if settings.test:
        return

    copies_h, copies_v, shifts = compute_actual_copies(context, Max_copies_h, Max_copies_v)
    print(f"Copies réelles HxV: {copies_h} x {copies_v}")
    print(f"Décalages par colonne (shiftlist): {shifts}")

    #nommage

    output_filename = compute_output_filename(args, context, copies_h, copies_v)

    print("Nom du fichier de sortie :", output_filename)

def main():
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()