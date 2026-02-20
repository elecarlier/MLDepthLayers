import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import logging

# ============================
# Configuration Logging
# ============================
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def inspect_mask(mask, name="mask"):
    """
    Affiche les informations essentielles d'un masque numpy et quelques pixels pour comprendre.
    Utile pour debug ou vérification rapide.
    """
    logger.info(f"--- Infos pour {name} ---")
    logger.info(f"Shape      : {mask.shape}")
    logger.info(f"Dtype      : {mask.dtype}")
    logger.info(f"Valeur min : {mask.min()}")
    logger.info(f"Valeur max : {mask.max()}")

    h, w = mask.shape
    logger.info(f"Premier pixel (0,0)   : {mask[0,0]}")
    logger.info(f"Pixel centre ({h//2},{w//2}): {mask[h//2, w//2]}")
    logger.info(f"Dernier pixel ({h-1},{w-1}): {mask[h-1, w-1]}")

# ============================
# Chargement des masques depuis les images
# ============================

masks_dir = "input/layers"  # dossier contenant les images originales
masks = {}  # dict : key = nom du fichier, value = masque numpy 2D avec valeurs 0-1

logger.debug(f"Lecture des images dans {masks_dir}...")

for filename in os.listdir(masks_dir):
    if not filename.lower().endswith(".png"):
        continue 

    path = os.path.join(masks_dir, filename)
    img = Image.open(path).convert("RGBA")  # conversion en RGBA pour récupérer le canal alpha

    # Extraction du canal alpha et normalisation entre 0 et 1
    alpha = np.array(img.split()[-1]).astype(np.float32) / 255.0

    # Création du masque binaire : pixels > 0.05 deviennent 1, sinon 0
    mask = (alpha > 0.05).astype(np.float32)

    # Optionnel : pour debug, afficher quelques infos
    # inspect_mask(mask, os.path.splitext(filename)[0])

    # Sauvegarde dans le dictionnaire
    name = os.path.splitext(filename)[0]
    masks[name] = mask


# ============================
# Visualisation rapide (facultative)
# ============================

plt.figure(figsize=(12, 4))
for i, (name, mask) in enumerate(masks.items()):
    plt.subplot(1, len(masks), i + 1)
    plt.imshow(mask, cmap="gray")
    plt.title(name)
    plt.axis("off")

# plt.show()  # Décommenter pour afficher les masques

# ============================
# Sauvegarde des masques
# ============================

output_dir = "output/masks"
os.makedirs(output_dir, exist_ok=True)

for name, mask in masks.items():
    # Conversion en image niveau de gris 8 bits
    mask_img = (mask * 255).astype(np.uint8)
    img = Image.fromarray(mask_img, mode="L")  # "L" = grayscale
    save_path = os.path.join(output_dir, f"{name}_mask.png")
    img.save(save_path)
    logger.debug(f"Masque sauvegardé : {save_path}")

