#!/usr/bin/env python3
"""
Batch runner pour générer les cartes de profondeur avec run.py
Traite toutes les images dans input/layers et sauvegarde les résultats dans output/depth_maps_layers
"""

import subprocess
from pathlib import Path
import os

import tifffile as tiff
import numpy as np
from PIL import Image



input_folder = Path("input/layers")
output_folder = Path("output/depth_maps_layers")
output_folder.mkdir(parents=True, exist_ok=True)

image_paths = list(input_folder.glob("*.*"))  # JPG, PNG, etc.




print(f"Found {len(image_paths)} images in {input_folder}")

image_ori_path = Path("input/images")

src_path = str(Path(__file__).parent / "src")

def load_image(path):
    img = Image.open(path)
    return np.array(img)


for image_path in image_paths:
    print(f"Processing {image_path.name} ...")
    subprocess.run([
        "python", "run.py",
        "-i", str(image_path),            
        "-o", str(output_folder),         
        "--skip-display"                  
    ])

print("All layers processed!")

print(f"Processing global {image_ori_path.name} ...")
subprocess.run([
    "python", "run.py",
    "-i", str(image_ori_path),            
    "-o", str(output_folder),         
    "--skip-display"                  
])

print("✅ All images processed!")


def load_image(path):
    return np.array(Image.open(path))

layer_dir = Path("output/depth_maps_layers")
output_tiff = Path("output/final") / "layers_stack.tif"

layer_images = sorted(layer_dir.glob("*.jpg"))

if not layer_images:
    raise RuntimeError(" No layer images found in output directory")

pages = [load_image(p) for p in layer_images]

photometric = "rgb" if pages[0].ndim == 3 else "minisblack"

tiff.imwrite(
    output_tiff,
    pages,
    photometric=photometric
)

print(f"✅ TIFF multipage créé : {output_tiff}")

