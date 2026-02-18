from pathlib import Path
from PIL import Image
from cli import parse_args
from models import PrintSettings, PrintContext
from layout import compute_max_copies, compute_actual_copies
from images_utils import trim_image, add_border

# --- Fonctions utilitaires de test ---

def run_test_case(
    mire_path, image_path,
    cols=0, rows=0,
    hcopies=-1, vcopies=-1,
    hpos=1, vpos=1,
    tile=False,
    makeshift=-1,
    shiftlist=None,
    trim=0, border=-1
):
    # Charger images
    mire = Image.open(mire_path)
    img2 = Image.open(image_path)

    # Créer settings et context
    settings = PrintSettings(
        cols=cols, rows=rows,
        hcopies=hcopies, vcopies=vcopies,
        hpos=hpos, vpos=vpos,
        tile=tile, makeshift=makeshift,
        trim_mm=trim, border_mm=border
    )
    context = PrintContext(settings, mire, img2)

    # Appliquer trim / border
    if trim > 0:
        img2 = trim_image(img2, trim, context)
        context.image_size = img2.size

    if border > 0:
        img2 = add_border(img2, border, context)
        context.image_size = img2.size

    # Valeurs max
    max_h, max_v = compute_max_copies(context)

    # Valeurs réelles
    copies_h, copies_v, shifts = compute_actual_copies(context, max_h, max_v)

    print(f"\n--- TEST ---")
    print(f"Mire: {mire_path}, Image: {image_path}")
    print(f"Max HxV: {max_h} x {max_v}")
    print(f"Copies réelles HxV: {copies_h} x {copies_v}")
    print(f"Décalages par colonne: {shifts}")

    # Fermer images
    mire.close()
    img2.close()


# --- Liste de tests ---
tests = [
    # Pavage normal sans contraintes
    ("/Users/eleonore/MLDepthLayers/mires/mires_templates/50.png", "/Users/eleonore/MLDepthLayers/mires/input/sirphe.tif"),

    # Pavage avec nombre de colonnes/rows forcé
    ("/Users/eleonore/MLDepthLayers/mires/mires_templates/50.png", "/Users/eleonore/MLDepthLayers/mires/input/sirphe.tif", 5, 4),

    # Pavage avec HCopies/VCopies
    ("/Users/eleonore/MLDepthLayers/mires/mires_templates/50.png", "/Users/eleonore/MLDepthLayers/mires/input/sirphe.tif", 0, 0, 3, 2, 1, 1, True),

    # Pavage avec position de départ
    ("/Users/eleonore/MLDepthLayers/mires/mires_templates/50.png", "/Users/eleonore/MLDepthLayers/mires/input/sirphe.tif", 0, 0, 4, 3, 2, 2, True),

    # Makeshift (mire de callage)
    ("/Users/eleonore/MLDepthLayers/mires/mires_templates/50.png", "/Users/eleonore/MLDepthLayers/mires/input/sirphe.tif", 0, 0, -1, -1, 1, 1, False, 5),

    # Shiftlist appliquée
    ("/Users/eleonore/MLDepthLayers/mires/mires_templates/50.png", "/Users/eleonore/MLDepthLayers/mires/input/sirphe.tif", 0, 0, 4, 3, 1, 1, True, -1, [0,1,2,3]),

    # Trim et border
    ("/Users/eleonore/MLDepthLayers/mires/mires_templates/50.png", "/Users/eleonore/MLDepthLayers/mires/input/sirphe.tif", 0, 0, -1, -1, 1, 1, False, -1, None, 2, 1),
]


# --- Exécution des tests ---
for test in tests:
    run_test_case(*test)
