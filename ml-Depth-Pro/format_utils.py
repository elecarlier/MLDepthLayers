from psd_tools import PSDImage
from pathlib import Path
from PIL import Image

import os
import shutil


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


def clean_name(filename):
    """
    Transforme :
    0000_Antenne_mask_isolated.png
    0000_Antenne_isolated.png

    en :
    Antenne.png
    """

    name = Path(filename).stem  # enlève .png

    # Supprime index (0000_)
    if "_" in name:
        name = name.split("_", 1)[1]

    # Supprime suffixes
    name = name.replace("_mask", "")
    name = name.replace("_isolated", "")

    return f"{name} map.png"


def export_final_folders(
    psd_path,
    isolated_global_dir="output/isolated_global",
    isolated_layers_dir="output/isolated_layers",
):
    """
    Crée deux dossiers dans le dossier du PSD :
        - global_map/
        - layers_map/

    Et copie les fichiers isolés en les renommant proprement.
    """

    psd_path = Path(psd_path)
    base_dir = psd_path.parent

    global_dir = base_dir / "global_map"
    layers_dir = base_dir / "layers_map"

    global_dir.mkdir(exist_ok=True)
    layers_dir.mkdir(exist_ok=True)

    # Nettoyage
    for f in global_dir.glob("*"):
        f.unlink()
    for f in layers_dir.glob("*"):
        f.unlink()

    # ---- GLOBAL ----
    for file in Path(isolated_global_dir).glob("*.png"):
        new_name = clean_name(file.name)
        shutil.copy(file, global_dir / new_name)

    # ---- LAYERS ----
    for file in Path(isolated_layers_dir).glob("*.png"):
        new_name = clean_name(file.name)
        shutil.copy(file, layers_dir / new_name)

    print("✅ Export final terminé.")
    print("📁 Global :", global_dir)
    print("📁 Layers :", layers_dir)


if __name__ == "__main__":
    # Extraction PSD -> PNG
    psd_to_png(Path("input/images/Escargot.psd"), Path("input/layers"))



