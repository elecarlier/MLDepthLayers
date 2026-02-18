from PIL import Image

class PrintSettings:
    """Paramètres fournis par l’utilisateur via CLI ou defaults."""
    def __init__(self, lpi=40.0, user_hdpi=720, user_vdpi=360,
                 trim_mm=0, border_mm=-1,
                 tile=False, makeshift=-1, cols=0, rows=0):
        self.lpi = lpi
        self.user_hdpi = user_hdpi
        self.user_vdpi = user_vdpi
        self.trim_mm = trim_mm
        self.border_mm = border_mm
        self.tile = tile
        self.makeshift = makeshift
        self.cols = cols
        self.rows = rows

    def __repr__(self):
        return (f"PrintSettings(lpi={self.lpi}, user_hdpi={self.user_hdpi}, "
                f"user_vdpi={self.user_vdpi}, trim_mm={self.trim_mm}, "
                f"border_mm={self.border_mm}, tile={self.tile}, "
                f"makeshift={self.makeshift}, cols={self.cols}, rows={self.rows})")


class PrintContext:
    """Paramètres calculés à partir des settings et des images."""
    def __init__(self, settings: PrintSettings, mire: Image.Image, image: Image.Image):
        # DPI
        self.hdpi = settings.user_hdpi
        self.vdpi = settings.user_vdpi

        # LPI et largeur de lentille en pixels
        self.lpi = settings.lpi
        self.lens_width_px = self.hdpi / self.lpi

        # Tailles de la mire
        self.mire_width, self.mire_height = mire.size

        # Taille de l'image à insérer
        self.image_width, self.image_height = image.size

        # Trim et border convertis en pixels
        self.trim_px_h = int(settings.trim_mm / 25.4 * self.hdpi)
        self.trim_px_v = int(settings.trim_mm / 25.4 * self.vdpi)
        self.border_px_h = int(settings.border_mm / 25.4 * self.hdpi) if settings.border_mm > 0 else 0
        self.border_px_v = int(settings.border_mm / 25.4 * self.vdpi) if settings.border_mm > 0 else 0

    def __repr__(self):
        return (f"PrintContext(hdpi={self.hdpi}, vdpi={self.vdpi}, lpi={self.lpi}, "
                f"lens_width_px={self.lens_width_px:.2f}, "
                f"mire_size=({self.mire_width},{self.mire_height}), "
                f"image_size=({self.image_width},{self.image_height}), "
                f"trim_px=({self.trim_px_h},{self.trim_px_v}), "
                f"border_px=({self.border_px_h},{self.border_px_v}))")
