import os
import cv2
import numpy as np

def isolate_from_masks(
    images_dir="output/final",
    fallback_dir="output/depth_maps_layers",
    masks_dir="output/masks",
    output_dir="output/isolated_global",
):
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(fallback_dir, exist_ok=True)
    os.makedirs(masks_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    global_images = [f for f in os.listdir(images_dir) if f.endswith("_map.jpg")]

    if global_images:
        image_path = os.path.join(images_dir, global_images[0])
    else:
        fallback_images = [f for f in os.listdir(fallback_dir) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
        if not fallback_images:
            raise ValueError(f"Aucune image trouvée ni dans {images_dir} ni dans {fallback_dir}")
        fallback_images.sort()
        image_path = os.path.join(fallback_dir, fallback_images[-1])
        print(f"Dossier final vide, utilisation de l'image fallback: {image_path}")

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Impossible de lire l'image {image_path}")

    for mask_name in os.listdir(masks_dir):
        mask_path = os.path.join(masks_dir, mask_name)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            print(f"Impossible de lire le masque {mask_name}")
            continue

        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        if image.shape[:2] != mask.shape[:2]:
            print(f"Taille différente pour {mask_name}, ignoré")
            continue

        b, g, r = cv2.split(image)
        rgba = cv2.merge([b, g, r, mask])

        output_name = os.path.splitext(mask_name)[0] + "_isolated.png"
        output_path = os.path.join(output_dir, output_name)
        cv2.imwrite(output_path, rgba)

    print("Isolation terminée.")


def isolate_single_depth(depth_path, mask_path, output_path):
    """
    Isole une seule depth map avec son masque correspondant.
    Pixels hors masque → totalement transparents.
    """

    depth = cv2.imread(depth_path, cv2.IMREAD_GRAYSCALE)
    if depth is None:
        raise ValueError(f"Impossible de lire {depth_path}")

    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError(f"Impossible de lire {mask_path}")

    _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

    if depth.shape != mask.shape:
        raise ValueError("Depth et masque tailles différentes")

    # Création RGBA
    rgba = np.zeros((depth.shape[0], depth.shape[1], 4), dtype=np.uint8)

    rgba[..., 0] = depth
    rgba[..., 1] = depth
    rgba[..., 2] = depth
    rgba[..., 3] = mask

    # Supprime réellement les pixels hors masque
    rgba[mask == 0] = [0, 0, 0, 0]

    cv2.imwrite(output_path, rgba)
    
def isolate_all_depths(
    depth_dir="output/depth_maps_layers",
    masks_dir="output/masks",
    output_dir="output/isolated_maps",
):
    """
    Applique l'isolation à toutes les depth maps trouvées.
    Matching automatique :
    layer_xxx_map.jpg → layer_xxx_mask.png
    """

    os.makedirs(output_dir, exist_ok=True)

    depth_files = [
        f for f in os.listdir(depth_dir)
        if f.endswith("_map.jpg")
    ]

    if not depth_files:
        raise ValueError("Aucune depth map trouvée")

    for depth_name in depth_files:

        base = depth_name.replace("_map.jpg", "")
        mask_name = f"{base}_mask.png"

        depth_path = os.path.join(depth_dir, depth_name)
        mask_path = os.path.join(masks_dir, mask_name)

        if not os.path.exists(mask_path):
            print(f"⚠️ Masque manquant pour {depth_name}")
            continue

        output_name = f"{base}_isolated.png"
        output_path = os.path.join(output_dir, output_name)

        isolate_single_depth(depth_path, mask_path, output_path)
        print(f"✔ Isolé : {output_name}")

    print("Isolation complète terminée.")

if __name__ == "__main__":
    isolate_from_masks()
    isolate_all_depths()