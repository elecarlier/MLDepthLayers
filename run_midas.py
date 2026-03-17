
#!/usr/bin/env python3
"""
Wrapper MiDaS pour MLDepthLayers.
Interface identique à run.py (Depth Pro) pour intégration dans le pipeline.

Copyright (C) 2024 Intel ISL — MiDaS
Modifications apportées par Eléonore Carlier
"""

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import PIL.Image
import torch
import cv2
from tqdm import tqdm
from matplotlib import pyplot as plt

LOGGER = logging.getLogger(__name__)

MIDAS_DIR = Path(__file__).parent / "Midas-Master_3.1"
sys.path.insert(0, str(MIDAS_DIR))

from midas.model_loader import load_model

# Mapping model_type → chemin absolu vers les poids
MIDAS_WEIGHTS = {
    "dpt_beit_large_512":  MIDAS_DIR / "weights" / "dpt_beit_large_512.pt",
    "dpt_hybrid_384":      MIDAS_DIR / "weights" / "dpt_hybrid-midas-501f0c75.pt",
    "dpt_large_384":       MIDAS_DIR / "weights" / "dpt_large-midas-2f21e586.pt",
    "dpt_swin2_large_384": MIDAS_DIR / "weights" / "dpt_swin2_large_384.pt",
    "midas_v21_384":       MIDAS_DIR / "weights" / "midas_v21-f6b98070.pt",
}


def get_torch_device() -> torch.device:
    device = torch.device("cpu")
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    return device


def read_image(path: Path) -> np.ndarray:
    """Lit une image en RGB float [0, 1]."""
    img = cv2.imread(str(path))
    if img is None:
        raise ValueError(f"Impossible de lire l'image : {path}")
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) / 255.0


def infer(device, model, model_type, image, net_w, net_h, target_size, transform):
    """Inférence MiDaS sur une image préparée. Retourne la depth map numpy."""
    prepared = transform({"image": image})["image"]
    sample = torch.from_numpy(prepared).to(device).unsqueeze(0)

    with torch.no_grad():
        prediction = model.forward(sample)
        prediction = (
            torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=target_size[::-1],
                mode="bicubic",
                align_corners=False,
            )
            .squeeze()
            .cpu()
            .numpy()
        )
    return prediction


def depth_to_uint8(depth: np.ndarray) -> np.ndarray:
    """Normalise la depth map en uint8 [0, 255]."""
    d_min, d_max = depth.min(), depth.max()
    if d_max > d_min:
        return ((depth - d_min) / (d_max - d_min) * 255).astype(np.uint8)
    return np.zeros_like(depth, dtype=np.uint8)


def run(args):
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    model_type = args.midas_type
    if model_type not in MIDAS_WEIGHTS:
        raise ValueError(f"Type inconnu : {model_type}. Choix : {list(MIDAS_WEIGHTS.keys())}")

    model_path = MIDAS_WEIGHTS[model_type]
    if not model_path.exists():
        raise FileNotFoundError(f"Poids introuvables : {model_path}")

    device = get_torch_device()
    LOGGER.info(f"Chargement MiDaS ({model_type}) sur {device}...")

    model, transform, net_w, net_h = load_model(device, str(model_path), model_type, optimize=False)

    image_paths = [args.image_path]
    if args.image_path.is_dir():
        exts = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
        image_paths = [p for p in args.image_path.glob("**/*") if p.suffix.lower() in exts]
        relative_path = args.image_path
    else:
        relative_path = args.image_path.parent

    for image_path in tqdm(image_paths):
        try:
            LOGGER.info(f"Processing {image_path} ...")
            original_image_rgb = read_image(image_path)
        except Exception as e:
            LOGGER.error(str(e))
            continue

        target_size = original_image_rgb.shape[1::-1]  # (width, height)
        depth = infer(device, model, model_type, original_image_rgb, net_w, net_h, target_size, transform)
        depth_uint8 = depth_to_uint8(depth)

        if args.output_path is not None:
            output_file = (
                args.output_path
                / image_path.relative_to(relative_path).parent
                / image_path.stem
            )
            output_file.parent.mkdir(parents=True, exist_ok=True)

            color_map_output_file = str(output_file) + "_map.jpg"
            PIL.Image.fromarray(depth_uint8).save(color_map_output_file, format="JPEG", quality=90)
            LOGGER.info(f"Sauvegardé : {color_map_output_file}")

            if args.side:
                img_uint8 = (original_image_rgb * 255).astype(np.uint8)
                depth_rgb = np.stack([depth_uint8] * 3, axis=2)
                side_by_side = np.concatenate((img_uint8, depth_rgb), axis=1)
                lkg_file = str(output_file) + "_lkg.jpg"
                PIL.Image.fromarray(side_by_side).save(lkg_file, format="JPEG", quality=90)
                LOGGER.info(f"Side-by-side sauvegardé : {lkg_file}")

    LOGGER.info("Done predicting depth!")


def main():
    parser = argparse.ArgumentParser(
        description="MiDaS depth estimation pour MLDepthLayers."
    )
    parser.add_argument("-i", "--image-path", type=Path, required=True,
                        help="Image ou dossier d'images en entrée.")
    parser.add_argument("-o", "--output-path", type=Path, default="output",
                        help="Dossier de sortie.")
    parser.add_argument("--skip-display", action="store_true", default=True)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Afficher les logs détaillés.")
    parser.add_argument("-s", "--side", action="store_true",
                        help="Générer une image côte à côte (original + depth map).")
    parser.add_argument("--midas-type",
                        choices=list(MIDAS_WEIGHTS.keys()),
                        default="dpt_hybrid_384",
                        help="Variante du modèle MiDaS (défaut : dpt_hybrid_384).")

    run(parser.parse_args())


if __name__ == "__main__":
    main()
