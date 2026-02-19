from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def paste_copies(mire, img2, context, copies_h, copies_v, shifts=None, erase=False):
    """
    Recopie img2 dans img1 selon le pavage calculé.
    
    Args:
        img1: Image de fond (la mire)
        img2: Image à recopier
        context: PrintContext avec infos sur DPI, lentille, etc.
        copies_h: nombre de colonnes à recopier
        copies_v: nombre de lignes à recopier
        shifts: liste des décalages horizontaux par colonne
        erase: bool, si True, on remplit la mire en blanc avant de recopier
    """
    if shifts is None:
        shifts = [0] * copies_h

    # Dimensions
    a1, b1 = mire.size
    a2, b2 = img2.size

    lens_width_px = context.lens_width_px
    centre_mire_h = mire.width // 2 

    # Efface la mire si demandé
    if erase:
        print("Effacement de la mire - remplir en blanc")
        mire.paste((255, 255, 255), (0, 0, a1, b1))

    print(f"Recopie {copies_h} colonnes x {copies_v} lignes")

    for H in range(copies_h):
        # Calcul du centre cible de la colonne H
        max_h = copies_h  # on utilise copies_h ici comme total de colonnes

        milieu_cible = int(a1 * ((2 * (H + context.hpos - 1) + 1) / (2 * copies_h)))

        a_debut_cible = int(milieu_cible - a2 / 2)

        # Ajustement pour alignement avec lentilles
        ecart_milieu = centre_mire_h - milieu_cible

        lentilles_ecart = int(ecart_milieu / lens_width_px)
        shift_cible = int(ecart_milieu - lentilles_ecart * lens_width_px)

        # Si shift spécifique par colonne
        shift_cible += shifts[H]

        a_debut = a_debut_cible + shift_cible

        for V in range(copies_v):
            b_debut = int(b1 * ((2 * V + 1) / (2 * copies_v)) - b2 / 2)
            mire.paste(img2, (a_debut, b_debut))


