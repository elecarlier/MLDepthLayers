from psd_tools import PSDImage
from pathlib import Path
from PIL import Image

# input_path = Path("input/images/Escargot.psd")
# output_folder = Path("output/psd")
# output_folder.mkdir(parents=True, exist_ok=True)

# psd = PSDImage.open(input_path)
# psd_width = psd.width
# psd_height = psd.height


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



# ---------------------------
# PNG -> PSD
# ---------------------------
# def png_to_psd_global(layers_dir: Path, depth_dir: Path, isolated_dir: Path,
#                       output_file: Path, reference_image: Path):
#     """
#     Crée un PSD unique à partir de 3 dossiers et adapte la taille à l'image globale.
#     Chaque trio (layer, map, mask) est ajouté dans le PSD dans l'ordre top = 0000.
#     """
#     # Taille du PSD = taille de la photo globale
#     ref_img = Image.open(reference_image)
#     canvas_width, canvas_height = ref_img.size
#     print(f"Taille PSD globale : {canvas_width}x{canvas_height}")

#     # Récupérer les fichiers triés par numéro
#     layers_files = sorted(layers_dir.glob("*.*"))
#     depth_files = sorted(depth_dir.glob("*.*"))
#     isolated_files = sorted(isolated_dir.glob("*.*"))

#     def clean_name(filepath):
#         name = filepath.stem
#         if "_" in name:
#             parts = name.split("_")
#             if parts[0].isdigit():
#                 name = "_".join(parts[1:])
#         name = name.replace("_map","").replace("_mask_isolated","")
#         return name

#     # Créer PSD vide
#     psd = PSD(width=canvas_width, height=canvas_height)

#     # Ajouter chaque trio layer/map/mask
#     for layer_file, depth_file, isolated_file in zip(layers_files, depth_files, isolated_files):
#         name = clean_name(layer_file)

#         layer_img = Image.open(layer_file).convert("RGBA")
#         depth_img = Image.open(depth_file).convert("RGBA")
#         isolated_img = Image.open(isolated_file).convert("RGBA")

#         # Ajouter layer principal
#         psd.add_layer(PSDWriterLayer.from_pil(layer_img, name=name))

#         # Ajouter depth map
#         psd.add_layer(PSDWriterLayer.from_pil(depth_img, name=name + "_map"))

#         # Ajouter mask isolé
#         psd.add_layer(PSDWriterLayer.from_pil(isolated_img, name=name + "_mask"))

#     # Sauvegarder le PSD
#     output_file.parent.mkdir(parents=True, exist_ok=True)
#     psd.save(output_file)
#     print(f"✅ PSD créé avec taille globale : {output_file}")


# ---------------------------
# Exemple d'utilisation
# ---------------------------
if __name__ == "__main__":
    # Extraction PSD -> PNG
    psd_to_png(Path("input/images/Escargot.psd"), Path("input/layers"))

    # # Création PSD depuis PNG
    # png_to_psd_global(
    #     layers_dir=Path("input/layers"),
    #     depth_dir=Path("output/depth_maps_layers"),
    #     isolated_dir=Path("output/isolated"),
    #     output_file=Path("output/final/layers_combined.psd"),
    #     reference_image=Path("input/images/Escargot.png")  # image globale pour taille PSD
    # )


