#!/usr/bin/env python3
"""
Batch runner pour générer les cartes de profondeur avec run.py
Traite toutes les images dans input/layers et sauvegarde les résultats dans output/depth_maps_layers
"""

import subprocess
from pathlib import Path

# Dossiers
input_folder = Path("input/layers")
output_folder = Path("output/depth_maps_layers")
output_folder.mkdir(parents=True, exist_ok=True)

# Liste toutes les images dans le dossier
image_paths = list(input_folder.glob("*.*"))  # JPG, PNG, etc.

print(f"Found {len(image_paths)} images in {input_folder}")

# Parcours de toutes les images
for image_path in image_paths:
    print(f"Processing {image_path.name} ...")
    # Appel de run.py via subprocess
    subprocess.run([
        "python", "run.py",
        "-i", str(image_path),            # image à traiter
        "-o", str(output_folder),         # dossier de sortie
        "--skip-display"                  # ne pas afficher les fenêtres matplotlib
    ])
print("✅ All images processed!")
