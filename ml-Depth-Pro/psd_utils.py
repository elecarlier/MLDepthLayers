from psd_tools import PSDImage
from pathlib import Path
from PIL import Image

input_path = Path("input/images/Escargot.psd")
output_folder = Path("output/psd")
output_folder.mkdir(parents=True, exist_ok=True)

psd = PSDImage.open(input_path)
psd_width = psd.width
psd_height = psd.height


def export_layers(layers, parent_name=""):
    for layer in layers:
        if not layer.is_visible():
            continue

        if layer.is_group():
            export_layers(layer, parent_name + layer.name + "_")
        else:
            layer_image = layer.composite()
            if layer_image:

                # 1️⃣ Créer une image vide à la taille du PSD
                full_image = Image.new("RGBA", (psd_width, psd_height), (0, 0, 0, 0))

                # 2️⃣ Récupérer la position du layer
                left, top, right, bottom = layer.bbox
                x, y = left, top


                # 3️⃣ Coller le layer à la bonne position
                full_image.paste(layer_image, (x, y), layer_image)

                layer_name = (parent_name + layer.name).replace("/", "_")
                output_path = output_folder / f"{layer_name}.png"
                full_image.save(output_path)

                print(f"Saved: {output_path}")

# Export de tous les layers
export_layers(psd)

# Export du rendu complet si besoin
psd.composite().save(output_folder / "Escargot_full.png")

#The opened PSD file can be saved:

#psdimage.save('output.psd')

