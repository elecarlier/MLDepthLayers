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

    if (args.cols == 0 or args.rows == 0) and str(image_path) != "Image_centree.tif":
        try:
                if args.makeshift <= 0:
                    # Mode normal : pas de mire de décalage
                    with Image.open(image_path, "r") as img:
                        TrimH = args.trim / 25.4 * Hdpi 
                        TrimV = args.trim / 25.4 * Vdpi

                        #tmpimage1 c'est la mire
                        # TrimValueH = args.trim/25.4*(TmpImage1.info.get('dpi', (args.HDPI, args.VDPI))[0])
                        # TrimValueV = args.trim/25.4*(TmpImage1.info.get('dpi', (args.HDPI, args.VDPI))[1])

                        if args.cols <= 0:
                            CopiesH = int(mire_img.size[0] / (img.size[0] - TrimH))
                        if args.rows <= 0:
                            CopiesV = int(mire_img.size[1] / (img.size[1] - TrimV))
                else:
                    # Mode mire de callage
                    CopiesH = args.makeshift 
                    CopiesV = Hdpi / args.LPI #pas nbr entier
        except IOError:
            print("Fichier mire ou image non trouvée")
            quit()

    return CopiesH, CopiesV