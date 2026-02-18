# image_utils.py

from PIL import Image, ImageOps
from pathlib import Path

def load_image(path):
    """
    Charge une image depuis le disque.
    """
    return Image.open(path, mode="r")


def get_dpi(image, default_hdpi, default_vdpi):
    """
    Récupère les DPI d'une image.

    Paramètres:
        image (PIL.Image)
        default_hdpi (int)
        default_vdpi (int)

    Retour:
        (hdpi, vdpi)
    """
    return image.info.get("dpi", (default_hdpi, default_vdpi))


def trim_image(img, trim_mm, hdpi, vdpi):
    """
    Supprime une bordure en millimètres autour de l'image.
    """
    if trim_mm <= 0:
        return img

    px_h = int(hdpi * trim_mm / 25.4)
    px_v = int(vdpi * trim_mm / 25.4)
        
    print("Trimming", px_h, px_v,"pixels")

    return img.crop((px_h, px_v, img.width - px_h, img.height - px_v))


def add_border(img, border_mm, hdpi, vdpi):
    """
    Ajoute une bordure noire autour de l'image.
    """
    if border_mm <= 0:
        return img

    px_h = int(hdpi * border_mm / 25.4)
    px_v = int(vdpi * border_mm / 25.4)

    print("Adding border of", px_h,px_v,"pixels")
    return ImageOps.expand(img, border=(px_h, px_v), fill=(0, 0, 0))

def load_and_prepare_image(file_path: Path, trim_mm=0, border_mm=-1, dpi=(720, 360)):
    """Charge et prépare l'image (trim, bord)."""
    img = load_image(file_path)
    if trim_mm > 0:
        img = trim_image(img, trim_mm, dpi[0], dpi[1])
    if border_mm > 0:
        img = add_border(img, border_mm, dpi[0], dpi[1])
    return img


def paste_images(img_bg, img_fg, copies_h, copies_v, max_h, max_v, hdpi, vdpi, h_pos=1, v_pos=1, shiftlist=None, erase=False):
    """Recopie img_fg sur img_bg selon le pavage demandé."""
    a_bg, b_bg = img_bg.size
    a_fg, b_fg = img_fg.size
    centre_h = int(a_bg / 2)

    if erase:
        img_bg.paste((255, 255, 255), (0, 0, a_bg, b_bg))

    for h in range(copies_h):
        # Calcul du centre cible
        mid_target = int(a_bg * ((2 * (h + h_pos - 1) + 1) / (2 * max_h)))
        start_x = mid_target - a_fg // 2

        # Décalage éventuel
        shift = 0
        if shiftlist and shiftlist[0] != -1:
            shift = shiftlist[h + h_pos - 1]
        start_x += shift

        for v in range(copies_v):
            start_y = int(b_bg * ((2 * (v + v_pos - 1) + 1) / (2 * max_v))) - b_fg // 2
            img_bg.paste(img_fg, (start_x, start_y))
    return img_bg

def compute_copies(img_bg, img_fg, hdpi, lpi, forced_cols=0, forced_rows=0, makeshift=-1):
    """Calcule le nombre maximal de copies et la largeur d'une lentille en pixels."""
    lens_width = compute_lens_width(hdpi, lpi)
    if makeshift <= 0:
        max_h, max_v = compute_max_copies(img_bg.size, img_fg.size, lens_width)
    else:
        max_h = makeshift
        max_v = int(lens_width)
    if forced_cols > 0:
        max_h = forced_cols
    if forced_rows > 0:
        max_v = forced_rows
    return lens_width, max_h, max_v


def resolve_dpi(image, user_hdpi: int, user_vdpi: int):
    """
    Détermine les DPI effectifs à utiliser.

    Priorité :
    1. DPI de l'image si présent
    2. Valeurs utilisateur si image sans DPI
    3. Écrasement explicite si utilisateur >= 0
    """
    
    hdpi, vdpi = image.info.get("dpi", (user_hdpi, user_vdpi))

    if user_hdpi >= 0:
        print("ecrasemnt")
        hdpi = user_hdpi
    if user_vdpi >= 0:
        vdpi = user_vdpi

    return hdpi, vdpi
