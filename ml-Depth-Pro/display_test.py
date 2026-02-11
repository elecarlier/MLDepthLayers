import matplotlib.image as mpimg
from pathlib import Path
import matplotlib.pyplot as plt
import tifffile as tiff
from PIL import Image


final_folder = Path("/Users/eleonore/MLDepthLayers/ml-Depth-Pro/output/final")

tiff_files = sorted(final_folder.glob("*.tif"))

if not tiff_files:
    raise RuntimeError(f"Aucun TIFF trouvé dans {final_folder}")

tiff_path = tiff_files[0]
print(f"Affichage du TIFF : {tiff_path}")


with tiff.TiffFile(tiff_path) as tif:
    print("Nombre total de pages :", len(tif.pages))
    print("Nombre de séries :", len(tif.series))
    for i, page in enumerate(tif.pages):
        img = page.asarray()

        # Si float > 1 → convertit en uint8
        if img.dtype.kind == "f" and img.max() > 1.0:
            img = img.astype("uint8")

        plt.figure(figsize=(5,5))
        if img.ndim == 2:
            plt.imshow(img, cmap="gray")
        else:
            plt.imshow(img)
        plt.title(f"Page {i}")
        plt.axis("off")
        plt.show()




