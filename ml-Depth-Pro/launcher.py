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

import argparse
import logging
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
# Configuration Logging
# ============================

def setup_logging(verbose=False):
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    
    # Masquer psd_tools info
    psd_logger = logging.getLogger("psd_tools")
    psd_logger.setLevel(logging.WARNING)
    
    # Masquer PIL info
    pil_logger = logging.getLogger("PIL")
    pil_logger.setLevel(logging.WARNING)
    
    return logger


logger = setup_logging()
psd_logger = logging.getLogger("psd_tools")
psd_logger.setLevel(logging.WARNING)  # ignore les messages “Unknown image resource”

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
def parse_arguments():

    parser = argparse.ArgumentParser(description="Launcher Depth Pro")
    parser.add_argument(
        "psd_path",
        type=Path,
        help="Chemin vers le fichier PSD à traiter"
    )
    parser.add_argument(
        "-s",
        "--side",
        action="store_true",
        help="Générer l'image side-by-side pour la globale"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Afficher les logs détaillés pendant l'exécution"
    )
    return parser.parse_args()


# ---------------------------
# Extraction PSD → PNG layers
# ---------------------------

def extract_layers(psd_path: Path):
    logger.info("Extraction des layers PSD → PNG")

    existing_layers_folder.mkdir(parents=True, exist_ok=True)

    # Nettoyage dossier
    for f in existing_layers_folder.glob("*"):
        f.unlink()

    psd_to_png(psd_path, existing_layers_folder)

    image_paths = sorted(existing_layers_folder.glob("*.png"))

    if not image_paths:
        logger.error("Aucun layer extrait du PSD")
        raise RuntimeError("Aucun layer extrait du PSD")

    logger.info(f"{len(image_paths)} layers extraits.")

    layer_files = sorted(existing_layers_folder.glob("*.*"))

    if not layer_files:
        logger.error("Aucune image trouvée.")
        raise RuntimeError("Aucune image trouvée.")

    global_image = layer_files[-1]
    logger.info(f"Image globale auto-définie : {global_image}")

    return image_paths, global_image


# ---------------------------
# Générer les masques avec generate_masks.py
# ---------------------------
"""
On lance le script generate_masks.py qui produit un masque binaire
pour chaque layer dans le dossier output/masks.
"""
def generate_masks():
    logger.info("Génération des masques...")

    subprocess.run(
        [sys.executable, "generate_masks.py", "--output", str(masks_dir)],
        check=True
    )

    logger.info("Masques générés dans output/masks")

    masks = {}

    for mask_file in masks_dir.glob("*.png"):
        name = mask_file.stem.replace("_mask", "")
        mask_img = Image.open(mask_file).convert("L")
        masks[name] = (np.array(mask_img) > 0).astype(np.uint8)

    logger.info(f"{len(masks)} masques chargés en mémoire.")
    return masks


# ---------------------------
# Génération des depth maps 
# ---------------------------
"""
Pour chaque layer PNG :
- On appelle run.py
- run.py génère une depth map correspondante
"""

def generate_depth_maps(image_paths):
    logger.info("Génération des cartes de profondeur...")

    for image_path in image_paths:
        logger.info(f"Processing {image_path.name}")

        subprocess.run([
            sys.executable,
            "run.py",
            "-i", str(image_path),
            "-o", str(output_folder),
            "--skip-display"
        ], check=True)

    logger.info("Cartes de profondeur générées.")

# ============================
# Isolation des depth maps par layer
# ============================

"""
On applique les masques aux depth maps afin d’obtenir :
- Une depth map isolée par layer
"""
def isolate_layers():
    logger.info("Isolation des depth maps par layer...")

    isolate_all_depths(
        depth_dir=output_folder,
        masks_dir=masks_dir,
        output_dir="output/isolated_layers"
    )

    logger.info("Isolation layers terminée.")


# ---------------------------
# Génération side-by-side pour la photo globale
# ---------------------------

"""
Si l'option -s est activée :
On génère une image combinée (original + depth map)
pour l'image globale uniquement.
"""

def generate_side_by_side(global_image: Path, final_folder: Path):
    logger.info("Génération side-by-side pour la photo globale")

    subprocess.run([
        sys.executable,
        "run.py",
        "-i", str(global_image),
        "-o", str(final_folder),
        "-s",
        "--skip-display"
    ], check=True)

    logger.info("Side-by-side généré.")



# ============================
# Export final des dossiers
# ============================

"""
On organise les résultats finaux dans une structure propre
à côté du PSD original.
"""
def export_results(psd_path: Path):
    logger.info("Création des dossiers finaux...")

    export_final_folders(
        psd_path=psd_path,
        isolated_global_dir="output/isolated_global",
        isolated_layers_dir="output/isolated_layers",
    )

    logger.info("Dossiers finaux prêts.")



def main():

    global logger
    args = parse_arguments() 


    logger = setup_logging(verbose=args.verbose)

    psd_path = args.psd_path
    do_side_by_side = args.side

    if not psd_path.exists():
        logger.error(f"Fichier introuvable : {psd_path}")
        raise RuntimeError(f"Fichier introuvable : {psd_path}")

    if psd_path.suffix.lower() != ".psd":
        logger.error("Le fichier fourni n'est pas un PSD")
        raise RuntimeError("Le fichier fourni n'est pas un PSD")

    logger.info(f"PSD reçu : {psd_path}")
    logger.info(f"Side-by-side activé : {do_side_by_side}")
    
    for d in [
        existing_layers_folder,
        output_folder,
        masks_dir,
        Path("output/isolated_global"),
        Path("output/isolated_layers"),
        Path("output/final")  # dossier central pour fallback
    ]:
        d.mkdir(parents=True, exist_ok=True)
        
    final_folder = psd_path.parent

    image_paths, global_image = extract_layers(psd_path)
    generate_masks()
    generate_depth_maps(image_paths)
    isolate_layers()

    if do_side_by_side:
        generate_side_by_side(global_image, final_folder)
    else:
        logger.warning("Side-by-side non généré (pas d'argument -s)")

    logger.info("Génération des cartes de profondeur isolées...")
    isolate_from_masks()
    logger.info("Cartes de profondeur isolées générées.")

    export_results(psd_path)

    logger.info("Pipeline terminé avec succès.")


if __name__ == "__main__":
    main()