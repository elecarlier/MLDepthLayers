from psd_tools import PSDImage
from pathlib import Path
from PIL import Image

# ---------------------------
# Export PSD -> PNG
# ---------------------------
def psd_to_png(input_psd: Path, output_folder: Path):
    """
    Extrait tous les layers d'un PSD en PNG dans output_folder.
    Les images gardent la taille du PSD et la position exacte des layers.
    """
    output_folder.mkdir(parents=True, exist_ok=True)
    psd = PSDImage.open(input_psd)
    psd_width, psd_height = psd.width, psd.height
    idx = 0

    def _export_layers(layers, parent_name=""):
        nonlocal idx
        for layer in reversed(layers):  # top layer en premier
            if not layer.is_visible():
                continue
            if layer.is_group():
                _export_layers(layer, parent_name + layer.name + "_")
            else:
                layer_image = layer.composite()
                if layer_image:
                    full_image = Image.new("RGBA", (psd_width, psd_height), (0,0,0,0))
                    left, top, right, bottom = layer.bbox
                    full_image.paste(layer_image, (left, top), layer_image)

                    filename = f"{idx:04d}_{parent_name}{layer.name}.png".replace("/", "_")
                    full_image.save(output_folder / filename)
                    print(f"Saved: {filename}")
                    idx += 1

    _export_layers(psd)



if __name__ == "__main__":
    # Extraction PSD -> PNG
    psd_to_png(Path("input/images/Escargot.psd"), Path("input/layers"))



