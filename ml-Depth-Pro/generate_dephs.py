import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

depth_path = "output/depth_maps/Le Syrphe Origine_map.jpg"           # Depth map globale
masks_dir = "output/masks"                # Masques déjà générés
output_dir = "output/depth_maps"          # Où sauvegarder les cartes de profondeur
os.makedirs(output_dir, exist_ok=True)




# depth_obj = depth * mask_obj 


# depth_final = maximum(depth_person, depth_table, depth_background)



# Plages de profondeur automatiques si tu veux toutes les cartes entre 0 et 1
default_range = (0.0, 1.0)


def remap(depth, min_val, max_val):
    """
    Remappe une depth map sur la plage [min_val, max_val]
    en prenant uniquement les pixels non nuls
    """
    d = depth.copy()
    mask_valid = d > 0
    if np.any(mask_valid):
        d_valid = d[mask_valid]
        d[mask_valid] = (d_valid - d_valid.min()) / (d_valid.max() - d_valid.min() + 1e-6)
        d[mask_valid] = d[mask_valid] * (max_val - min_val) + min_val
    return d

def load_masks(mask_dir):
    """
    Charge tous les masques d'un dossier et retourne un dictionnaire {nom: mask_array}
    """
    masks = {}
    for filename in os.listdir(mask_dir):
        if filename.lower().endswith(".png"):
            path = os.path.join(mask_dir, filename)
            img = Image.open(path).convert("L")  # niveau de gris
            mask = np.array(img).astype(np.float32) / 255.0  # 0-1
            name = os.path.splitext(filename)[0]  # nom du fichier sans extension
            masks[name] = mask
    return masks

# -----------------------------
# 3️⃣ Charger depth map et masques
# -----------------------------
depth_global = np.array(Image.open(depth_path).convert("L")).astype(np.float32) / 255.0

masks = load_masks(masks_dir)

# -----------------------------
# 4️⃣ Créer les cartes de profondeur individuelles
# -----------------------------
depth_maps = {}
for name, mask in masks.items():
    depth_masked = depth_global * mask
    
    # Remap automatique de 0-1
    depth_masked = remap(depth_masked, *default_range)
    
    depth_maps[name] = depth_masked
    
    # Sauvegarder chaque carte
    save_path = os.path.join(output_dir, f"{name}_depth.png")
    Image.fromarray((depth_masked * 255).astype(np.uint8)).save(save_path)

# -----------------------------
# 5️⃣ Fusionner les cartes
# -----------------------------
depth_final = np.maximum.reduce(list(depth_maps.values()))
final_path = os.path.join(output_dir, "depth_final.png")
Image.fromarray((depth_final * 255).astype(np.uint8)).save(final_path)

# -----------------------------
# 6️⃣ Affichage pour vérification
# -----------------------------
plt.figure(figsize=(15, 5))
for i, (name, dmap) in enumerate(depth_maps.items()):
    plt.subplot(1, len(depth_maps)+1, i+1)
    plt.imshow(dmap, cmap="viridis")
    plt.title(name)
    plt.axis("off")

plt.subplot(1, len(depth_maps)+1, len(depth_maps)+1)
plt.imshow(depth_final, cmap="viridis")
plt.title("Final Depth")
plt.axis("off")
plt.show()