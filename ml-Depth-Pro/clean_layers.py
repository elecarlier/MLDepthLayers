import os
import cv2
import numpy as np

INPUT_DIR = "input/layers_expanded"
OUTPUT_DIR = "input/layers_cleaned"

os.makedirs(OUTPUT_DIR, exist_ok=True)

THRESH = 10

for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(".png"):
        path = os.path.join(INPUT_DIR, filename)
        
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

        if img is None:
            print(f"{filename} non chargé")
            continue

        # Si grayscale → on ignore
        if len(img.shape) == 2:
            print(f"{filename} ignoré (grayscale)")
            continue

        # Si RGB → on ajoute un alpha plein
        if img.shape[2] == 3:
            rgb = img
            alpha = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255

        # Si RGBA
        elif img.shape[2] == 4:
            rgb = img[:, :, :3]
            alpha = img[:, :, 3]

        else:
            print(f"{filename} format inconnu")
            continue

        # Détection noir
        black_mask = np.all(rgb < THRESH, axis=2)

        alpha[black_mask] = 0

        result = np.dstack((rgb, alpha))

        output_path = os.path.join(OUTPUT_DIR, filename)
        cv2.imwrite(output_path, result)

print("Nettoyage terminé.")
