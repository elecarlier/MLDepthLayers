#!/usr/bin/env python3
"""
Launcher complet pour générer des cartes de profondeur.

Deux modes :
1️⃣ L'utilisateur fournit un TIFF multipage → chaque page devient un PNG dans `layers_folder`.
2️⃣ L'utilisateur fournit déjà un dossier de calques PNG/JPG → utilisé tel quel.

Ensuite :
- Chaque calque est traité par run.py
- Les depth maps générées sont regroupées dans un TIFF multipage final
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


layers_folder = Path("input/layers_from_tiff")          # calques extraits si TIFF
existing_layers_folder = Path("input/layers")           # calques existants

# output_folder_dilated = Path("output/depth_maps_dilated")
output_folder = Path("output/depth_maps_layers")
final_folder = Path("output/final")
masks_dir = Path("output/masks")                        # Les masques générés par generate_masks.py


output_folder.mkdir(parents=True, exist_ok=True)
final_folder.mkdir(parents=True, exist_ok=True)
masks_dir.mkdir(parents=True, exist_ok=True)




images_folder = Path("input/images")
image_files = sorted(images_folder.glob("*.*"))

# --------------------------------------------------
# Cas 1 : une image globale existe dans input/images
# --------------------------------------------------
if image_files:
    global_image = image_files[0]
    print(f"Image globale trouvée : {global_image}")

# --------------------------------------------------
# Cas 2 : aucune image globale → on prend la dernière layer
# --------------------------------------------------
else:
    print("Aucune image dans input/images.")
    print("Utilisation de la dernière image du dossier input/layers comme globale.")

    layer_files = sorted(existing_layers_folder.glob("*.*"))

    if not layer_files:
        raise RuntimeError("Aucune image trouvée ni dans input/images ni dans input/layers.")

    global_image = layer_files[-1]  # dernière image alphabétique
    print(f"Image globale auto-définie : {global_image}")


# ---------------------------
# Detection du mode
# ---------------------------
if global_image.suffix.lower() in [".tif", ".tiff"]:
    print(f"TIFF détecté : {global_image}, extraction des pages...")
    tiff_to_pngs(global_image, layers_folder)
    processing_folder = layers_folder

# Mode photo globale PNG/JPG
else:
    print(f"Photo globale détectée : {global_image}")
    # Les calques existants + la photo globale
    #changing to exp
    processing_folder = existing_layers_folder
    extra_images = [global_image]


image_paths = sorted(processing_folder.glob("*.*"))
if global_image.suffix.lower() not in [".tif", ".tiff"]:
    image_paths += extra_images  # ajoute la photo globale aux calques
if not image_paths:
    raise RuntimeError("Aucun fichier à traiter !")

print(f"Found {len(image_paths)} images à traiter.")


# ---------------------------
# Générer les masques avec generate_masks.py
# ---------------------------

print("✅ Génération des masques...")
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
print("✅ Génération des cartes de profondeur...")
for image_path in image_paths:
    print(f"Processing {image_path.name} ...")

    # Génération depth map
    depth_path = output_folder / f"{image_path.stem}_map.jpg"
    subprocess.run([
        sys.executable, "run.py",
        "-i", str(image_path),
        "-o", str(output_folder),
        "--skip-display"
    ])

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

# mettre en option 
print("Génération side-by-side pour la photo globale")

subprocess.run([
    sys.executable, "run.py",
    "-i", str(global_image),
    "-o", str(final_folder),
    "-s",                
    "--skip-display"
])


# ---------------------------
# Génération des depth maps isolées
# ---------------------------
print("✅ Génération des cartes de profondeur isolées...")

isolate_from_masks()

# ---------------------------
# Création TIFF multipage final
# ---------------------------

# def load_image(path):
#     return np.array(Image.open(path))

# # Récupérer toutes les images générées
# layer_images = sorted(output_folder.glob("*.*"))
# layer_images = [p for p in layer_images if p.suffix.lower() in [".png", ".jpg", ".jpeg"]]

# if not layer_images:
#     raise RuntimeError("❌ Aucun fichier depth map trouvé pour créer le TIFF multipage")


# pages = [load_image(p) for p in layer_images]
# photometric = "rgb" if pages[0].ndim == 3 else "minisblack"

# output_tiff = final_folder / "layers_stack.tif"
# tiff.imwrite(
#     output_tiff,
#     pages,
#     photometric=photometric,
#     bigtiff=True  # ✅ permet de dépasser la limite de 4 Go
# )

# print(f"✅ TIFF multipage final créé : {output_tiff}")

print("Terminé")