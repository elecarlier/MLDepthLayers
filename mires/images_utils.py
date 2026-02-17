# image_utils.py

from PIL import Image, ImageOps


def load_image(path):
    """
    Charge une image depuis le disque.

    Paramètres:
        path (Path | str): chemin du fichier image

    Retour:
        PIL.Image.Image
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

    return img.crop((px_h, px_v, img.width - px_h, img.height - px_v))


def add_border(img, border_mm, hdpi, vdpi):
    """
    Ajoute une bordure noire autour de l'image.
    """
    if border_mm <= 0:
        return img

    px_h = int(hdpi * border_mm / 25.4)
    px_v = int(vdpi * border_mm / 25.4)

    return ImageOps.expand(img, border=(px_h, px_v), fill=(0, 0, 0))
