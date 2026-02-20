import os
import cv2
import numpy as np

def dilate_images(input_dir="output/depth_maps_layers",
                  output_dir="output/depth_maps_dilated",
                  scale=1.15):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".jpg"):
            path = os.path.join(input_dir, filename)
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

            h, w = img.shape[:2]

            new_w = int(w * scale)
            new_h = int(h * scale)
            scaled = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

            canvas = np.zeros_like(img)

            x_offset = (w - new_w) // 2
            y_offset = (h - new_h) // 2

            x1 = max(0, -x_offset)
            y1 = max(0, -y_offset)

            x2 = min(new_w, w - x_offset)
            y2 = min(new_h, h - y_offset)

            canvas[
                max(0, y_offset):max(0, y_offset)+(y2-y1),
                max(0, x_offset):max(0, x_offset)+(x2-x1)
            ] = scaled[y1:y2, x1:x2]

            output_path = os.path.join(output_dir, filename)
            success = cv2.imwrite(output_path, canvas)
            if not success:
                print("Erreur sauvegarde :", output_path)

    print("Scale propre terminé.")


if __name__ == "__main__":
    dilate_images()