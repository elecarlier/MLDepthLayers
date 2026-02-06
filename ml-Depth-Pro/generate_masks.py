import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt



# Charger depth map (exportée par Depth Pro)
# depth = np.array(Image.open("Output/depth.png")).astype(np.float32)

def inspect_mask(mask, name="mask"):
    """
    Affiche les infos essentielles d'un masque numpy et quelques pixels pour comprendre.
    """
    print(f"--- Infos pour {name} ---")

    print("Shape :", mask.shape)  
    print("Dtype :", mask.dtype)  
    print("Valeur min :", mask.min())
    print("Valeur max :", mask.max())

    h, w = mask.shape
    print(f"Premier pixel (0,0) : {mask[0,0]}")
    print(f"Pixel centre ({h//2},{w//2}) : {mask[h//2, w//2]}")
    print(f"Dernier pixel ({h-1},{w-1}) : {mask[h-1, w-1]}")


masks_dir = "input/masks"
#key -> le nom du fichier 
# value -> tableau numpy 2D avec valeurs 0-1

masks = {}

for filename in os.listdir(masks_dir):
    if not filename.lower().endswith(".png"):
        continue

    path = os.path.join(masks_dir, filename)
    img = Image.open(path).convert("RGBA")

    alpha = np.array(img.split()[-1]).astype(np.float32) / 255.0

    mask = (alpha > 0.05).astype(np.float32)
    # mask = alpha


    name = os.path.splitext(filename)[0]
    masks[name] = mask
    inspect_mask(mask, name)

plt.figure(figsize=(12, 4))

for i, (name, mask) in enumerate(masks.items()):
    plt.subplot(1, len(masks), i + 1)
    plt.imshow(mask, cmap="gray")
    plt.title(name)
    plt.axis("off")

plt.show()


output_dir = "output/masks"
os.makedirs(output_dir, exist_ok=True)

for name, mask in masks.items():
    mask_img = (mask * 255).astype(np.uint8)
    img = Image.fromarray(mask_img, mode="L")  # "L" = niveau de gris
    img.save(os.path.join(output_dir, f"{name}_mask.png"))


# Charger masque (noir & blanc)
# mask = np.array(Image.open("input/masks/person.png").convert("L")) / 255.0

# #ici ca va générer 3 cartes de prof comme on a 3 maskes
# depth_person = depth * mask
# depth_table = depth * mask_table
# depth_background = depth * mask_background


# def remap(depth, min_val, max_val):
#     d = depth.copy()
#     d = (d - d.min()) / (d.max() - d.min() + 1e-6)
#     return d * (max_val - min_val) + min_val


# depth_person = remap(depth_person, 0.7, 1.0)
# depth_table = remap(depth_table, 0.4, 0.7)
# depth_background = remap(depth_background, 0.0, 0.4)


# depth_final = np.maximum.reduce([
#     depth_person,
#     depth_table,
#     depth_background
# ])
