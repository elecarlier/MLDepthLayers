import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# # Charger l'image PNG
# img = mpimg.imread('/Users/eleonore/MLDepthLayers/ml-Depth-Pro/input/images/Le Syrphe Origine.png')  # Remplace par le chemin de ton fichier

# # Afficher l'image
# plt.imshow(img)       # imshow gère les couleurs automatiquement
# plt.axis('off')       # Optionnel : pour ne pas afficher les axes
# plt.show()
from pathlib import Path
import matplotlib.pyplot as plt
import tifffile as tiff
from PIL import Image

# img_path = Path("/Users/eleonore/MLDepthLayers/ml-Depth-Pro/input/images/Le Syrphe Simplifie LS.tif")

#img_path = Path("/Users/eleonore/MLDepthLayers/ml-Depth-Pro/output/depth_maps_layers/layers_stack.tif")

# img = tiff.imread("/Users/eleonore/MLDepthLayers/ml-Depth-Pro/input/images/Le Syrphe Simplifie LS.tif")
# print(img.shape, img.dtype)


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

# for i in range(img.shape[0]):
#     plt.figure(figsize=(5,5))
#     plt.imshow(img[i], cmap='gray' if img[i].ndim == 2 else None)
#     plt.title(f"Stack {i}")
#     plt.axis("off")
#     plt.show()
#Pour la Syrphe -> (3987, 5949, 3) uint8





# #ok but shows in png
# im = Image.open("/Users/eleonore/MLDepthLayers/ml-Depth-Pro/input/images/Le Syrphe Simplifie LS.tif")
# im.show()


# #works but     from skimage import io
# #ModuleNotFoundError: No module named 'skimage'
# from skimage import io
# import matplotlib.pyplot as plt

# # read the image stack
# img = io.imread("/Users/eleonore/MLDepthLayers/ml-Depth-Pro/input/images/Le Syrphe Simplifie LS.tif")
# # show the image
# plt.imshow(img,cmap='gray')
# plt.axis('off')
# # save the image
# plt.savefig('output.tif', transparent=True, dpi=300, bbox_inches="tight", pad_inches=0.0)



#to save a numpy array as a tif file
#tifffile.imwrite('my_image.tif', my_numpy_data, photometric='rgb')
#or
#tifffile.imsave('my_image.tif', my_numpy_data)
