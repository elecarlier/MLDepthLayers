import os
import cv2

def isolate_from_masks(
    images_dir="output/final",   # dossier contenant l'image globale
    masks_dir="output/masks",
    output_dir="output/isolated",
):
    """
    Isole des parties d'une image globale à partir de plusieurs masques
    et crée un PNG avec transparence (fond transparent là où le masque est noir).
    """

    os.makedirs(output_dir, exist_ok=True)

    # Trouver l'image globale qui finit par _map.jpg
    global_images = [f for f in os.listdir(images_dir) if f.endswith("_map.jpg")]
    if not global_images:
        raise ValueError(f"Aucune image globale (_map.jpg) trouvée dans {images_dir}")
    
    image_path = os.path.join(images_dir, global_images[0])
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Impossible de lire l'image {image_path}")

    # Parcourir les masques
    for mask_name in os.listdir(masks_dir):
        mask_path = os.path.join(masks_dir, mask_name)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            print(f"Impossible de lire le masque {mask_name}")
            continue

        # Binariser le masque
        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        # Vérifier dimensions
        if image.shape[:2] != mask.shape[:2]:
            print(f"Taille différente pour {mask_name}, ignoré")
            continue

        # Créer le résultat avec canal alpha
        b, g, r = cv2.split(image)
        rgba = cv2.merge([b, g, r, mask])  # le masque devient le canal alpha

        # Sauvegarder le PNG transparent
        output_name = os.path.splitext(mask_name)[0] + "_isolated.png"
        output_path = os.path.join(output_dir, output_name)
        cv2.imwrite(output_path, rgba)

    print("Isolation terminée.")


if __name__ == "__main__":
    isolate_from_masks()