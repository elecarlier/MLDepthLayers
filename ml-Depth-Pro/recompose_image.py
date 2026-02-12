from PIL import Image
from pathlib import Path

layers_folder = Path("input/layers")
layer_paths = sorted(layers_folder.glob("*.png"))

# On ouvre le premier calque pour définir la taille
base_layer = Image.open(layer_paths[0]).convert("RGBA")
final_image = Image.new("RGBA", base_layer.size, (0, 0, 0, 0))  # vide au départ

for layer_path in layer_paths:
    layer = Image.open(layer_path).convert("RGBA")
    # On colle seulement là où il y a des pixels non transparents
    final_image.paste(layer, (0, 0), mask=layer)

final_image.save("output/reconstructed.png")
print("✅ Image reconstruite correctement !")