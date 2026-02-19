from psd_tools import PSDImage
from pathlib import Path
from PIL import Image
import logging

# ============================
# Logger
# ============================
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.getLogger("psd_tools").setLevel(logging.WARNING)

# ---------------------------
# Export PSD -> PNG
# ---------------------------
def psd_to_png(input_psd: Path):
    """
    Extrait tous les layers visibles d'un PSD en PNG
    dans le dossier mires_templates en gardant leurs noms d'origine.
    """
    psd = PSDImage.open(input_psd)
    psd_width, psd_height = psd.width, psd.height
    output_folder = input_psd.parent  # même dossier que le PSD

    def _export_layers(layers):
        for layer in layers:
            if not layer.is_visible():
                continue

            if layer.is_group():
                _export_layers(layer)
            else:
                layer_image = layer.composite()
                if layer_image:
                    full_image = Image.new("RGBA", (psd_width, psd_height), (0, 0, 0, 0))
                    left, top, right, bottom = layer.bbox
                    full_image.paste(layer_image, (left, top), layer_image)
                    safe_name = layer.name.replace("/", "_").replace("\\", "_")
                    filename = f"{safe_name}.png"

                    full_image.save(output_folder / filename)
                    logger.info(f"Saved: {filename}")

    _export_layers(psd)


if __name__ == "__main__":
    psd_path = Path("/Users/eleonore/MLDepthLayers/mires/mires_templates/Mires Compendium.psd")
    psd_to_png(psd_path)
