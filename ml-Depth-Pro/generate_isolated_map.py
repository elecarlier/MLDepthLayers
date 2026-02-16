import os
import cv2

def isolate_from_masks(
    images_dir="output/final",
    fallback_dir="output/depth_maps_layers",
    masks_dir="output/masks",
    output_dir="output/isolated",
):
    os.makedirs(output_dir, exist_ok=True)

    global_images = [f for f in os.listdir(images_dir) if f.endswith("_map.jpg")]

    if global_images:
        image_path = os.path.join(images_dir, global_images[0])
    else
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


if __name__ == "__main__":
    isolate_from_masks()