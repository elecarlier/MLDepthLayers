import cv2
import numpy as np

# chemins des fichiers
img_path = "/Users/eleonore/MLDepthLayers/ml-Depth-Pro/input/images/Le Syrphe Origine.png"
mask_path = "/Users/eleonore/MLDepthLayers/ml-Depth-Pro/input/layers/_0000_Abeille.png"

# lire les images
img = cv2.imread(img_path)
mask = cv2.imread(mask_path, 0)  # 0 = lecture en grayscale

# vérification rapide
assert img is not None, "Image non chargée"
assert mask is not None, "Masque non chargé"

# bounding box du masque
ys, xs = np.where(mask > 0)
x1, x2 = xs.min(), xs.max()
y1, y2 = ys.min(), ys.max()

# marge (contexte autour de l'abeille)
margin = 40
h, w = img.shape[:2]
x1 = max(0, x1 - margin)
y1 = max(0, y1 - margin)
x2 = min(w, x2 + margin)
y2 = min(h, y2 + margin)

crop = img[y1:y2, x1:x2]

# 🔹 Zoom sans déformation
# On calcule le facteur pour que l'abeille remplisse ~80% du crop final
final_size = 512  # taille finale de l'image zoomée
crop_h, crop_w = crop.shape[:2]

# facteur pour garder le ratio
scale = final_size / max(crop_h, crop_w)

# nouvelle taille
new_w = int(crop_w * scale)
new_h = int(crop_h * scale)

# redimensionner
crop_zoomed = cv2.resize(crop, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

# créer une image carrée finale avec fond noir
canvas = np.zeros((final_size, final_size, 3), dtype=np.uint8)

# calcul position pour centrer le crop
start_x = (final_size - new_w) // 2
start_y = (final_size - new_h) // 2

canvas[start_y:start_y+new_h, start_x:start_x+new_w] = crop_zoomed

# sauvegarde
cv2.imwrite("crop_abeille_zoom.png", canvas)
print("Crop zoomé généré : crop_abeille_zoom.png")
