import os
import cv2
import numpy as np

INPUT_DIR = "input/layers"
OUTPUT_DIR = "input/layers_expanded"
EXPAND_PIXELS = 60  # taille d’agrandissement

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        path = os.path.join(INPUT_DIR, filename)
        
        mask = cv2.imread(path, cv2.IMREAD_UNCHANGED)

        # Si masque RGBA → on récupère alpha
        if mask.shape[-1] == 4:
            alpha = mask[:, :, 3]
        else:
            alpha = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        # Binarisation propre
        _, binary = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)

        # Dilatation
        kernel = np.ones((EXPAND_PIXELS, EXPAND_PIXELS), np.uint8)
        expanded = cv2.dilate(binary, kernel, iterations=1)

        output_path = os.path.join(OUTPUT_DIR, filename)
        cv2.imwrite(output_path, expanded)

print("Expansion terminée.")
