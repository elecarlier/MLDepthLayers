


def resolve_dpi(image, user_hdpi: int, user_vdpi: int):
    """
    Détermine les DPI effectifs.
    Priorité utilisateur si >= 0.
    """
    img_hdpi, img_vdpi = image.info.get("dpi", (user_hdpi, user_vdpi))

    if user_hdpi >= 0:
        img_hdpi = user_hdpi

    if user_vdpi >= 0:
        img_vdpi = user_vdpi

    return img_hdpi, img_vdpi
