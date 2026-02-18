#!/usr/bin/env python3
from PIL import Image

from cli import parse_args
from models import PrintSettings, PrintContext
from dpi import resolve_dpi
from images_utils import trim_image, add_border
from layout import compute_max_copies


def test_all():
    args = parse_args()

    print("=== Test 1 : Parser ===")
    print(args)

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
    print("=== Test 2 : PrintSettings ===")
    print(settings)

    # Charger la mire
    mire = Image.open(args.mire)
    hdpi, vdpi = resolve_dpi(mire, settings.user_hdpi, settings.user_vdpi)
    context = PrintContext(hdpi, vdpi, settings.lpi)
    print("=== Test 3 : PrintContext ===")
    print(f"HDPI: {context.hdpi}, VDPI: {context.vdpi}, Lens width px: {context.lens_width_px}")

    # Charger image à insérer
    img2 = Image.open(args.image)

    if settings.trim_mm > 0:
        img2_trim = trim_image(img2, settings.trim_mm, context)
        print(f"Trimmed image size: {img2_trim.size}")

    if settings.border_mm > 0:
        img2_border = add_border(img2, settings.border_mm, context)
        print(f"Bordered image size: {img2_border.size}")

    max_h, max_v = compute_max_copies(mire.size, img2.size, context)
    print(f"=== Test 4 : Max copies HxV === {max_h} x {max_v}")

    # Fermer les images
    mire.close()
    img2.close()


if __name__ == "__main__":
    test_all()
