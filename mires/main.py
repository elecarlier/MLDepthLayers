#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
from cli import parse_args
from models import PrintSettings, PrintContext
from images_utils import trim_image, add_border
from layout import compute_max_copies, compute_actual_copies
from output import compute_output_filename
from action_image import paste_copies
from adjustment_mire import create_alignment_mire



def run(args):

    # ============================
    # Configuration 
    # ============================

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

    Image.MAX_IMAGE_PIXELS = None  # éviter warning grandes images ancienne valeur 2052314995

    mire = Image.open(args.mire)
    img2 = Image.open(args.image)
    context = PrintContext(settings, mire, img2)

    print("=== Settings ===")
    print(settings)
    print("=== Context ===")
    print(context)

    # ============================
    # Mode création mire d'ajustement
    # ============================

    if settings.makeshift > 0:
        print("Mode : création d'une mire d'ajustement")
        output_file = create_alignment_mire(args, context, mire.copy())
        print("Mire d'ajustement générée :", output_file)
        mire.close()
        img2.close()
        return
    
    # ============================
    # Mode normal
    # ============================

    if settings.trim_mm > 0:
        img2 = trim_image(img2, context)

    
    context.image_size = img2.size #mise à jour 

    if settings.border_mm > 0:
        img2 = add_border(img2, context)

    context.image_size = img2.size #mise à jour 

    # Calcul du nombre maximal de copies
    Max_copies_h, Max_copies_v = compute_max_copies(context)
    print(f"Max Copies HxV: {Max_copies_h} x {Max_copies_v}")

    if settings.test:
        return

    copies_h, copies_v, shifts = compute_actual_copies(context, Max_copies_h, Max_copies_v)

    print(f"Copies réelles HxV: {copies_h} x {copies_v}")
    print(f"Décalages par colonne (shiftlist): {shifts}")

    output_filename = compute_output_filename(args, context, copies_h, copies_v)
    paste_copies(mire, img2, context, copies_h, copies_v, shifts=shifts, erase=False)
    
    mire.save(output_filename)    
    print("Nom du fichier de sortie :", output_filename)

    mire.close()
    img2.close()
    
def main():
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()