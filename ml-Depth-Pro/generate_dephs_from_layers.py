import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# -----------------------------
# 1️⃣ Configurations
# -----------------------------
layers_dir = "input/layers_dir"          # Dossier contenant les calques des éléments
output_dir = "output/depth_maps"      # Où sauvegarder les cartes de profondeur
os.makedirs(output_dir, exist_ok=True)

default_range = (0.0, 1.0)            # Plage de profondeur automatique

# -----------------------------
# 2️⃣ Fonctions utilitaires
# -----------------------------
def remap(depth, min_val, max_val):
    """
    Remappe une carte de profondeur sur [min_val, max_val]
    en prenant uniquement les pixels non nuls
    """
    d = depth.copy()
    mask_valid = d > 0
    if np.any(mask_valid):
        d_valid = d[mask_valid]
        d[mask_valid] = (d_valid - d_valid.min()) / (d_valid.max() - d_valid.min() + 1e-6)
        d[mask_valid] = d[mask_valid] * (max_val - min_val) + min_val
    return d

def load_layers(layers_dir):
    """
    Charge les calques d'un dossier et retourne un dictionnaire {nom: layer_depth}
    Chaque calque doit être en PNG/JPG avec fond transparent ou noir.
    """
    layers = {}
    for filename in os.listdir(layers_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(layers_dir, filename)
            img = Image.open(path).convert("RGBA")  # RGBA pour conserver transparence
            alpha = np.array(img.split()[-1]).astype(np.float32) / 255.0  # alpha 0-1
            rgb = np.array(img.convert("L")).astype(np.float32) / 255.0   # intensité du calque
            layer_depth = rgb * alpha
            name = os.path.splitext(filename)[0]
            layers[name] = layer_depth
    return layers

# -----------------------------
# 3️⃣ Charger calques
# -----------------------------
layers = load_layers(layers_dir)

# -----------------------------
# 4️⃣ Créer les cartes de profondeur individuelles
# -----------------------------
depth_maps = {}
for name, layer_depth in layers.items():
    depth_masked = remap(layer_depth, *default_range)
    depth_maps[name] = depth_masked

    # Sauvegarde de la carte individuelle
    save_path = os.path.join(output_dir, f"{name}_depth.png")
    Image.fromarray((depth_masked * 255).astype(np.uint8)).save(save_path)

# -----------------------------
# 5️⃣ Fusionner toutes les cartes
# -----------------------------
if depth_maps:
    depth_final = np.maximum.reduce(list(depth_maps.values()))
    final_path = os.path.join(output_dir, "depth_final.png")
    Image.fromarray((depth_final * 255).astype(np.uint8)).save(final_path)
else:
    print("⚠️ Aucun calque trouvé dans", layers_dir)
    depth_final = None

# -----------------------------
# 6️⃣ Affichage pour vérification
# -----------------------------
plt.figure(figsize=(15, 5))
for i, (name, dmap) in enumerate(depth_maps.items()):
    plt.subplot(1, len(depth_maps)+1, i+1)
    plt.imshow(dmap, cmap="viridis")
    plt.title(name)
    plt.axis("off")

if depth_final is not None:
    plt.subplot(1, len(depth_maps)+1, len(depth_maps)+1)
    plt.imshow(depth_final, cmap="viridis")
    plt.title("Final Depth")
    plt.axis("off")

plt.show()
