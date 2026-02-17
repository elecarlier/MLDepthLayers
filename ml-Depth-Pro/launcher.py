#!/usr/bin/env python3
"""
Launcher principal pour générer des cartes de profondeur à partir d’un PSD

Pipeline complet :
1. Extraction des layers du PSD en PNG
2. Génération des masques
3. Génération des depth maps pour chaque layer
4. Isolation des depth maps par masque
5. (Optionnel) Génération d'une image side-by-side pour la globale
6. Export final des dossiers structurés
"""


# ============================
# Imports des modules internes
# ============================

from dilate_image import dilate_images #optionnel

from generate_isolated_map import (
    isolate_from_masks,
    isolate_all_depths,
)
import subprocess
from pathlib import Path
import tifffile as tiff
from PIL import Image
import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion, distance_transform_edt
import sys
from format_utils import psd_to_png, export_final_folders

# ============================
# Définition des dossiers
# ============================

existing_layers_folder = Path("input/layers")       # Dossier de travail contenant les layers PNG     
output_folder = Path("output/depth_maps_layers")    # Dossier de sortie pour les depth maps générées
masks_dir = Path("output/masks")                    # Dossier de sortie pour les masques générés


# Création des dossiers si inexistants
output_folder.mkdir(parents=True, exist_ok=True)
masks_dir.mkdir(parents=True, exist_ok=True)

# ---------------------------
# Parsing arguments CLI
# ---------------------------
"""
Arguments attendus :
- Chemin vers un fichier PSD (obligatoire)
- Option -s (facultative) : active la génération side-by-side
"""
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

final_folder = psd_path.parent # Le dossier final correspond au dossier contenant le PSD
print(f"Dossier final : {final_folder}")

# ---------------------------
# Extraction PSD → PNG layers
# ---------------------------
"""
On convertit chaque layer du PSD en image PNG.
On vide d'abord le dossier pour éviter d'utiliser d'anciens fichiers.
"""

existing_layers_folder.mkdir(parents=True, exist_ok=True)

for f in existing_layers_folder.glob("*"):
    f.unlink()

psd_to_png(psd_path, existing_layers_folder)

processing_folder = existing_layers_folder
image_paths = sorted(processing_folder.glob("*.png"))

if not image_paths:
    raise RuntimeError("❌ Aucun layer extrait du PSD")

print(f"✅ {len(image_paths)} layers extraits.")


# On considère la dernière image (alphabétiquement) comme image globale
layer_files = sorted(existing_layers_folder.glob("*.*"))

if not layer_files:
    raise RuntimeError("Aucune image trouvée.")

global_image = layer_files[-1]  # dernière image alphabétique
print(f"Image globale auto-définie : {global_image}")


print(f"Found {len(image_paths)} images à traiter.")


# ---------------------------
# Générer les masques avec generate_masks.py
# ---------------------------
"""
On lance le script generate_masks.py qui produit un masque binaire
pour chaque layer dans le dossier output/masks.
"""

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
"""
Pour chaque layer PNG :
- On appelle run.py
- run.py génère une depth map correspondante
"""

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

# ============================
# Isolation des depth maps par layer
# ============================

"""
On applique les masques aux depth maps afin d’obtenir :
- Une depth map isolée par layer
"""

print("Isolation des depth maps par layer...")

isolate_all_depths(
    depth_dir=output_folder,
    masks_dir=masks_dir,
    output_dir="output/isolated_layers"
)

print("✅ Isolation layers terminée.")


# ---------------------------
# Génération side-by-side pour la photo globale
# ---------------------------

"""
Si l'option -s est activée :
On génère une image combinée (original + depth map)
pour l'image globale uniquement.
"""

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


# ============================
# Export final des dossiers
# ============================

"""
On organise les résultats finaux dans une structure propre
à côté du PSD original.
"""

print("Création des dossiers finaux...")

export_final_folders(
    psd_path=psd_path,
    isolated_global_dir="output/isolated_global",
    isolated_layers_dir="output/isolated_layers",
)

print("✅ Dossiers finaux prêts.")

print("Terminé")