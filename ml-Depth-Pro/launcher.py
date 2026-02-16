#!/usr/bin/env python3
"""
Launcher complet pour générer des cartes de profondeur.

"""


from dilate_image import dilate_images
from generate_isolated_map import isolate_from_masks
import subprocess
from pathlib import Path
import tifffile as tiff
from PIL import Image
import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion, distance_transform_edt
import sys
from format_utils import psd_to_png 


layers_folder = Path("input/layers_from_tiff")          # calques extraits si TIFF
existing_layers_folder = Path("input/layers")           # calques existants
output_folder = Path("output/depth_maps_layers")
masks_dir = Path("output/masks")                        # Les masques générés par generate_masks.py

output_folder.mkdir(parents=True, exist_ok=True)
masks_dir.mkdir(parents=True, exist_ok=True)

# ---------------------------
# Parsing arguments 
# ---------------------------

args = sys.argv[1:]

do_side_by_side = False
psd_path = None

for arg in args:
    if arg == "-s":
        do_side_by_side = True
    else:
        psd_path = Path(arg)

if psd_path is None:
    raise RuntimeError("❌ Tu dois fournir le chemin vers un fichier PSD")

if not psd_path.exists():
    raise RuntimeError(f"❌ Fichier introuvable : {psd_path}")

if psd_path.suffix.lower() != ".psd":
    raise RuntimeError("❌ Le fichier fourni n'est pas un PSD")

print(f"PSD reçu : {psd_path}")
print(f"Side-by-side activé : {do_side_by_side}")

final_folder = psd_path.parent
print(f"Dossier final : {final_folder}")

# ---------------------------
# Extraction PSD → PNG layers
# ---------------------------
existing_layers_folder.mkdir(parents=True, exist_ok=True)

for f in existing_layers_folder.glob("*"):
    f.unlink()

psd_to_png(psd_path, existing_layers_folder)

processing_folder = existing_layers_folder
image_paths = sorted(processing_folder.glob("*.png"))

if not image_paths:
    raise RuntimeError("❌ Aucun layer extrait du PSD")

print(f"✅ {len(image_paths)} layers extraits.")

print("Utilisation de la dernière image du dossier input/layers comme globale.")

layer_files = sorted(existing_layers_folder.glob("*.*"))

if not layer_files:
    raise RuntimeError("Aucune image trouvée ni dans input/images ni dans input/layers.")

global_image = layer_files[-1]  # dernière image alphabétique
print(f"Image globale auto-définie : {global_image}")


image_paths = sorted(processing_folder.glob("*.*"))

if not image_paths:
    raise RuntimeError("Aucun fichier à traiter !")

print(f"Found {len(image_paths)} images à traiter.")


# ---------------------------
# Générer les masques avec generate_masks.py
# ---------------------------

print("Génération des masques...")
subprocess.run([sys.executable, "generate_masks.py", "--output", str(masks_dir)])
print("✅ Masques générés dans", masks_dir)

masks = {}
for mask_file in masks_dir.glob("*.png"):
    name = mask_file.stem.replace("_mask", "")
    mask_img = Image.open(mask_file).convert("L")
    masks[name] = (np.array(mask_img) > 0).astype(np.uint8)


# ---------------------------
# Génération des depth maps 
# ---------------------------
print("Génération des cartes de profondeur...")
for image_path in image_paths:
    print(f"Processing {image_path.name} ...")

    depth_path = output_folder / f"{image_path.stem}_map.jpg"
    subprocess.run([
        sys.executable, "run.py",
        "-i", str(image_path),
        "-o", str(output_folder),
        "--skip-display"
    ])
print("✅ Cartes de profondeur générées dans", output_folder)

# ---------------------------
# Dilatation des depths maps 
# ---------------------------
# dilate_images()

# Ou avec des paramètres personnalisés
# dilate_images(
#     input_dir="mes_images/input",
#     output_dir="mes_images/output",
#     scale=1.2
#)


# ---------------------------
# Génération side-by-side pour la photo globale
# ---------------------------
if do_side_by_side:
    print("Génération side-by-side pour la photo globale")
    subprocess.run([
        sys.executable, "run.py",
        "-i", str(global_image),
        "-o", str(final_folder),
        "-s",                
        "--skip-display"
    ])
else:
    print("⚠️ Side-by-side non généré (pas d'argument -s)")


# ---------------------------
# Génération des depth maps isolées
# ---------------------------
print("Génération des cartes de profondeur isolées...")

isolate_from_masks()

print("✅ Cartes de profondeur isolées générées dans", output_folder)



print("Terminé")