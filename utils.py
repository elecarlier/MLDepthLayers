


def depth_to_uint8(depth):
    """Convertit une depth map float en uint8 0-255"""
    depth_min, depth_max = depth.min(), depth.max()
    if depth_max - depth_min == 0:
        return (depth * 255).astype(np.uint8)
    norm = (depth - depth_min) / (depth_max - depth_min)
    return (norm * 255).astype(np.uint8)


def expand_depth_inside(depth_map_path, mask, expand_px=60, interior_px=15):
    depth = np.array(Image.open(depth_map_path)).astype(np.float32)
    if depth.max() > 1:
        depth /= 255.0

    # Dilater le masque pour créer le halo
    dilated_mask = binary_dilation(mask, iterations=expand_px)
    halo_pixels = dilated_mask & (~mask)

    # distance transform depuis le **bord de l'objet**
    dist, indices = distance_transform_edt(mask == 0, return_indices=True)

    # pour chaque pixel du halo, on prend le pixel dans l'objet à distance interior_px
    halo_y, halo_x = np.where(halo_pixels)
    for y, x in zip(halo_y, halo_x):
        iy, ix = indices[:, y, x]  # pixel le plus proche dans l'objet
        # maintenant on remonte dans l'objet interior_px pixels
        dy = iy - y
        dx = ix - x
        norm = np.sqrt(dy**2 + dx**2)
        if norm == 0:
            continue
        # on calcule un point à distance interior_px dans l'objet
        factor = interior_px / norm
        iy_new = int(round(y + dy * factor))
        ix_new = int(round(x + dx * factor))
        # clamp pour rester dans l'image
        iy_new = np.clip(iy_new, 0, mask.shape[0]-1)
        ix_new = np.clip(ix_new, 0, mask.shape[1]-1)
        # appliquer seulement si on est dans l'objet
        if mask[iy_new, ix_new]:
            depth[y, x] = depth[iy_new, ix_new]

    return Image.fromarray((depth * 255).astype(np.uint8))


def dilate_image(image_path, expand_px=5):
    """
    Dilate l'objet dans l'image de 'expand_px' pixels.
    image_path : Path vers l'image PNG
    expand_px : nombre de pixels pour dilater
    Retourne un PIL.Image
    """
    img = Image.open(image_path).convert("RGBA")
    alpha = np.array(img.split()[-1])  # canal alpha
    mask = alpha > 0  # True = objet, False = fond

    # Dilate le masque
    dilated_mask = binary_dilation(mask, iterations=expand_px)

    # Crée une nouvelle image avec le masque dilaté
    new_alpha = (dilated_mask * 255).astype(np.uint8)
    img.putalpha(Image.fromarray(new_alpha))
    return img


def tiff_to_pngs(tiff_path, output_folder):
    """
    Fonction de conversionn TFF -> PNG
    """
    output_folder.mkdir(parents=True, exist_ok=True)

    with tiff.TiffFile(tiff_path) as tif:
        for i, page in enumerate(tif.pages):
            img = page.asarray()
            if img.dtype.kind == "f":
                img = np.clip(img, 0, 255).astype(np.uint8) if img.max() > 1 else (img*255).astype(np.uint8)
            elif img.dtype == np.uint16:
                img = (img/256).astype(np.uint8)
            Image.fromarray(img).save(output_folder / f"page_{i:03d}.png")

    print(f"✅ {len(tif.pages)} pages extracted to {output_folder}")
