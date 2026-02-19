import pytest
from PIL import Image
from pathlib import Path
from mires.main import run  # ⚡ Import corrigé

def test_full_pipeline_smoke(tmp_path):
    """
    Test minimal du pipeline complet sans utiliser de vraies images.
    Crée temporairement une mire et une image à insérer.
    Vérifie que le fichier de sortie est créé.
    """

    # Créer une mire factice 200x200 pixels
    mire_path = tmp_path / "dummy_mire.tif"
    Image.new("RGB", (200, 200), color="white").save(mire_path)

    # Créer une image à insérer 50x50 pixels
    image_path = tmp_path / "dummy_image.tif"
    Image.new("RGB", (50, 50), color="gray").save(image_path)

    # Définir le fichier de sortie
    output_path = tmp_path / "output.png"

    # Construire les arguments simulés
    class Args:
        mire = mire_path
        image = image_path
        output = output_path
        addfile = "Non renseigné"
        LPI = 40.0
        HDPI = 300
        VDPI = 300
        HCopies = -1
        VCopies = -1
        VPos = 1
        HPos = 1
        rows = 0
        cols = 0
        tile = False
        erase = False
        trim = 0
        border = -1
        add = False
        test = False
        makeshift = -1
        shiftlist = (-1, -1)

    # Lancer la fonction run avec les arguments factices
    run(Args)

    # Vérifier que le fichier de sortie a bien été créé
    assert output_path.exists()
    # Optionnel : vérifier que l'image a bien la taille de la mire
    with Image.open(output_path) as out_img:
        assert out_img.size == (200, 200)
