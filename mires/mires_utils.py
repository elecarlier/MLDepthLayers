from PIL import Image
from pathlib import Path

def calculate_copies(mire_path, image_path, args):
    """
    Calcule le nombre de copies horizontales et verticales
    à placer sur la mire si cols/rows ne sont pas forcés.

    Retourne : CopiesH, CopiesV
    """
    CopiesH = args.cols
    CopiesV = args.rows

    # On ne fait le calcul que si cols ou rows ne sont pas renseignés
    if (args.cols == 0 or args.rows == 0) and str(image_path) != "Image_centree.tif":
        try:
            with Image.open(mire_path, "r") as mire_img:
                Hdpi = mire_img.info.get('dpi', (args.HDPI, args.VDPI))[0]
                Vdpi = mire_img.info.get('dpi', (args.HDPI, args.VDPI))[1]

                if args.HDPI >= 0:
                    Hdpi = args.HDPI
                if args.VDPI >= 0:
                    Vdpi = args.VDPI

                if args.makeshift <= 0:
                    # Mode normal : on utilise l'image à insérer
                    with Image.open(image_path, "r") as img:
                        TrimH = args.trim / 25.4 * Hdpi
                        TrimV = args.trim / 25.4 * Vdpi

                        if args.cols <= 0:
                            CopiesH = int(mire_img.size[0] / (img.size[0] - TrimH))
                        if args.rows <= 0:
                            CopiesV = int(mire_img.size[1] / (img.size[1] - TrimV))
                else:
                    # Mode mire de callage
                    CopiesH = args.makeshift
                    CopiesV = int(Hdpi / args.LPI)
        except IOError:
            print("Fichier mire ou image non trouvée")
            quit()

    return CopiesH, CopiesV