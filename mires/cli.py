import argparse
from pathlib import Path

def parse_args():
    """Définition des arguments CLI."""
    parser = argparse.ArgumentParser(description="Assemblage et alignement images sur une mire centrée.")
    parser.add_argument(
        "-m", 
        "--mire", 
        type=Path, 
        default="/Users/eleonore/MLDepthLayers/mires/mires_templates/50.png",
        help="Nom du fichier Frame"
    )
    parser.add_argument(
        "-i",
        "--image",
        type=Path,
        default="/Users/eleonore/MLDepthLayers/mires/input/sirphe.tif",
        help="Path/Nom du fichier à insérer."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Nom du fichier à créer. \nCalcule automatiquement un nom si non renseigné"
    )
    parser.add_argument(
        "-a",
        "--addfile",
        type=Path,
        default=None,
        help="Nom du fichier à ajouter"
    )
    parser.add_argument(
        "--LPI",
        type=float,
        default=50.0,
        help="Linéature apparente de la plaque (40.0 par défaut)."
    )
    parser.add_argument(
        "--HDPI",
        type=int,
        default=720,
        help="Résolution horizontale d'impression."
    )
    parser.add_argument(
        "--VDPI",
        type=int,
        default=360,
        help="Résolution verticale d'impression."
    )
    parser.add_argument(
        "--HCopies", 
        type=int,
        default=-1,
        help="Nombre de copies horizontales."
    )
    parser.add_argument(
        "--VCopies", 
        type=int,
        default=-1,
        help="Nombre de copies verticales."
    )
    parser.add_argument(
        "--VPos", 
        type=int,
        default=1,
        help="Position de début des copies de 1 à N. Vaut 1 par défaut"
    )
    parser.add_argument(
        "--HPos", 
        type=int,
        default=1,
        help="Position de début des copies de 1 à N. Vaut 1 par défaut"
    )
    parser.add_argument(
        "--rows", 
        type=int,
        default=0,
        help="Force le nombre de lignes d'image"
    )
    parser.add_argument(
        "--cols", 
        type=int,
        default=0,
        help="Force le nombre de colonnes"
    )
    parser.add_argument(
        "--tile",
        action="store_true",
        default=False, 
        help="cree un pavage si présent, une seule copie centrée sinon."
    )
    parser.add_argument(
        "--erase",
        action="store_true",
        default=False, 
        help="Efface la mire si présent."
    )
    parser.add_argument(
        "--trim",
        type=int,
        default=0, 
        help="Enlève [trim] mm de bord de l'image à recopier."
    )
    parser.add_argument(
        "--border",
        type=int,
        default=-1, 
        help="Ajoute un bord noir de [border] à l'image à recopier."
    )
    parser.add_argument(
        "--add",
        action="store_true",
        default=False, 
        help="Ajoute l'image aux précedentes dans le fichier Output."
    )
    parser.add_argument(
        "--test",
        action="store_true",
        default=False, 
        help="Calcule le nombre d'images qu'il est possible de caser dans la mire, puis quitte le programme"
    )
    parser.add_argument(
        "--makeshift",
        type=int,
        default=-1, 
        help="Si positif, imprime une mire pour ajuster les positions des [nombre] colonnes"
    )
    parser.add_argument(
        "--shiftlist",
        nargs="+",
        type=int,
        default=(-1,-1),
        help="Liste les décalages à appliquer aux différentes colonnes (liste de valeurs entieres sans virgules)"
    )
    # run(parser.parse_args())

    return parser.parse_args()