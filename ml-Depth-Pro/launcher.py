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

import subprocess
from pathlib import Path
import tifffile as tiff
from PIL import Image
import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion
import sys



layers_folder = Path("input/layers_from_tiff")          # calques extraits si TIFF
existing_layers_folder = Path("input/layers")           # calques existants

#output_folder_dilated = Path("output/dilated")
output_folder = Path("output/depth_maps_layers")
final_folder = Path("output/final")
masks_dir = Path("output/masks")                        # Les masques générés par generate_masks.py


output_folder.mkdir(parents=True, exist_ok=True)
final_folder.mkdir(parents=True, exist_ok=True)
masks_dir.mkdir(parents=True, exist_ok=True)


def depth_to_uint8(depth):
    """Convertit une depth map float en uint8 0-255"""
    depth_min, depth_max = depth.min(), depth.max()
    if depth_max - depth_min == 0:
        return (depth * 255).astype(np.uint8)
    norm = (depth - depth_min) / (depth_max - depth_min)
    return (norm * 255).astype(np.uint8)

def expand_depth_inside(depth_map_path, mask, expand_px=60, interior_px=30, boost=0.0, use_mean=True):
    """
    Dilate la depth map autour de l'objet, en prenant les pixels à l'intérieur pour calculer le halo.
    boost : ajout à la valeur moyenne intérieure (float), pas nécessairement 255 max.
    """
    # Charge en float
    depth = np.array(Image.open(depth_map_path)).astype(np.float32)
    
    # Si depth est en 0-255, on normalise en 0-1 pour travailler
    if depth.max() > 1:
        depth = depth / 255.0

    # Dilater le masque pour créer le halo
    dilated_mask = binary_dilation(mask, iterations=expand_px)
    halo_pixels = dilated_mask & (mask == 0)

    # Erosion pour choisir les pixels à l'intérieur
    interior_mask = binary_erosion(mask, iterations=interior_px)

    if interior_mask.sum() == 0:
        value = depth[mask == 1].mean()
    else:
        value = depth[interior_mask].mean() if use_mean else depth[interior_mask].max()

    # value = min(value + boost, 1.0)  # reste dans 0-1

    # Appliquer au halo
    depth[halo_pixels] = value

    # Retour à uint8 pour image finale
    depth_uint8 = (depth * 255).astype(np.uint8)
    return Image.fromarray(depth_uint8)


# def expand_depth_with_mask(depth_map_path, mask, expand_px=60, use_mean=True):
#     depth = np.array(Image.open(depth_map_path)).astype(np.float32)
#     dilated_mask = binary_dilation(mask, iterations=expand_px)
#     new_pixels = dilated_mask & (mask == 0)
#     # new_pixels = dilated_mask & (mask == 1)  # étendre l'objet
#     value = depth[mask == 1].mean() if use_mean else depth[mask == 1].max()
#     depth[new_pixels] = value
#     return Image.fromarray(depth.astype(np.uint8))

def dilate_image(image_path, expand_px=5):
    """
    Dilate l'objet dans l'image de 'expand_px' pixels.
    image_path : Path vers l'image PNG
    expand_px : nombre de pixels pour dilater
    Retourne un PIL.Image
    """
    img = Image.open(image_path).convert("RGBA")
    alpha = np.array(img.split()[-1])  # canal alpha
    mask = alpha > 0  # True = objet, False = fond

    # Dilate le masque
    dilated_mask = binary_dilation(mask, iterations=expand_px)

    # Crée une nouvelle image avec le masque dilaté
    new_alpha = (dilated_mask * 255).astype(np.uint8)
    img.putalpha(Image.fromarray(new_alpha))
    return img

#Fonction de conversionn TFF -> PNG
def tiff_to_pngs(tiff_path, output_folder):
    output_folder.mkdir(parents=True, exist_ok=True)

    with tiff.TiffFile(tiff_path) as tif:
        for i, page in enumerate(tif.pages):
            img = page.asarray()
            if img.dtype.kind == "f":
                img = np.clip(img, 0, 255).astype(np.uint8) if img.max() > 1 else (img*255).astype(np.uint8)
            elif img.dtype == np.uint16:
                img = (img/256).astype(np.uint8)
            Image.fromarray(img).save(output_folder / f"page_{i:03d}.png")

    print(f"✅ {len(tif.pages)} pages extracted to {output_folder}")

images_folder = Path("input/images")
image_files = sorted(images_folder.glob("*.*"))
if not image_files:
    raise RuntimeError("Aucun fichier trouvé dans input/images")

# On prend le premier fichier trouvé
global_image = image_files[0]

# Detection du mode
if global_image.suffix.lower() in [".tif", ".tiff"]:
    print(f"TIFF détecté : {global_image}, extraction des pages...")
    tiff_to_pngs(global_image, layers_folder)
    processing_folder = layers_folder

# Mode photo globale PNG/JPG
else:
    print(f"Photo globale détectée : {global_image}")
    # Les calques existants + la photo globale
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
# Génération des depth maps + dilation
# ---------------------------
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

    # Appliquer dilation avec le masque si disponible
    mask_name = image_path.stem
    if mask_name in masks:
        # expanded_depth = expand_depth_with_mask(depth_path, masks[mask_name], expand_px=60)
        expanded_depth = expand_depth_inside(depth_path, masks[mask_name], expand_px=60, interior_px=40)

        
        # Nouveau nom pour la map dilatée
        dilated_path = output_folder / f"{image_path.stem}_map_dilated.png"
        expanded_depth.save(dilated_path)
        print(f"✅ Depth map dilatée enregistrée : {dilated_path}")
    else:
        print(f"⚠️ Aucun masque trouvé pour {mask_name}")

# ---------------------------
#Traitement avec run.py
# ---------------------------

# #test
# for image_path in image_paths:
#     print(f"Processing {image_path.name} ...")

#     # --- Dilate le calque pour que la depth map dépasse légèrement ---
    
#     #iterations=expand_px -> pixel de dilatation
#     dilated_img = dilate_image(image_path, expand_px=60)  
#     temp_path = output_folder_dilated / f"dilated_{image_path.name}"
#     dilated_img.save(temp_path)

#     print(f"✅ Envoi à run.py : {temp_path}")
#     print(f"Existe ? {temp_path.exists()}")

#     # --- Passe la dilatée à run.py ---
#     subprocess.run([
#         "python", "run.py",
#         "-i", str(temp_path),
#         "-o", str(output_folder_dilated),
#         "--skip-display"
#     ])



# # src_path = str(Path(__file__).parent / "src")  # si run.py nécessite un chemin src

# # for image_path in image_paths:
# #     print(f"Processing {image_path.name} ...")
# #     subprocess.run([
# #         "python", "run.py",
# #         "-i", str(image_path),
# #         "-o", str(output_folder),
# #         "--skip-display"
# #     ])

print("✅ Toutes les layers traitées !")

# ---------------------------
# Création TIFF multipage final
# ---------------------------

def load_image(path):
    return np.array(Image.open(path))

# Récupérer toutes les images générées
layer_images = sorted(output_folder.glob("*.*"))
layer_images = [p for p in layer_images if p.suffix.lower() in [".png", ".jpg", ".jpeg"]]

if not layer_images:
    raise RuntimeError("❌ Aucun fichier depth map trouvé pour créer le TIFF multipage")


pages = [load_image(p) for p in layer_images]
photometric = "rgb" if pages[0].ndim == 3 else "minisblack"

output_tiff = final_folder / "layers_stack.tif"
tiff.imwrite(
    output_tiff,
    pages,
    photometric=photometric,
    bigtiff=True  # ✅ permet de dépasser la limite de 4 Go
)

print(f"✅ TIFF multipage final créé : {output_tiff}")

