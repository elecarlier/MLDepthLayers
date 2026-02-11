import os
import cv2
import numpy as np

INPUT_DIR = "input/layers"
OUTPUT_DIR = "input/layers_expanded"
SCALE = 1.15  # 15% plus grand

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if filename.lower().endswith(".jpg"):
        path = os.path.join(INPUT_DIR, filename)
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

        h, w = img.shape[:2]

        # Resize complet (RGBA inclus)
        new_w = int(w * SCALE)
        new_h = int(h * SCALE)
        scaled = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Créer canvas original
        canvas = np.zeros_like(img)

        # Centrage
        x_offset = (w - new_w) // 2
        y_offset = (h - new_h) // 2

        # Si l'image dépasse → on crop proprement
        x1 = max(0, -x_offset)
        y1 = max(0, -y_offset)

        x2 = min(new_w, w - x_offset)
        y2 = min(new_h, h - y_offset)

        canvas[
            max(0, y_offset):max(0, y_offset)+(y2-y1),
            max(0, x_offset):max(0, x_offset)+(x2-x1)
        ] = scaled[y1:y2, x1:x2]

        output_path = os.path.join(OUTPUT_DIR, filename)
        success = cv2.imwrite(output_path, canvas)
        if not success:
            print("Erreur sauvegarde :", output_path)

print("Scale propre terminé.")
