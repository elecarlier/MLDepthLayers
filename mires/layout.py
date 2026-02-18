
from models import PrintSettings, PrintContext

def compute_max_copies(context: PrintContext, test_mode: bool = False):

    """
    Calcule le nombre maximal de copies d'une image sur la mire.
    
    Prend en compte :
        - trim et border déjà appliqués (taille effective de l'image)
        - pavage horizontal avec marge pour lentille
        - overrides user (cols, rows)
        - makeshift mode (mire de callage)
        - test_mode: si True, affiche et quitte

    Returns:
        copies_h, copies_v : int
    """
     # Taille effective de l'image après trim/border. (normalmement déjà mis à jour dans main)
    effective_w = context.image_width
    effective_h = context.image_height


    # Cas classique : pas de mire de callage
    if context.makeshift <= 0:
        max_h = int(context.mire_width / (effective_w + context.lens_width_px + 1))
        max_v = int(context.mire_height / effective_h)
    else:
        max_h = context.makeshift
        max_v = int(context.lens_width_px)
    

    # Valeurs par défaut : on ne dépasse jamais le max
    copies_h = max_h
    copies_v = max_v


    # Mode test : afficher et quitter
    if test_mode:
        print(f"Nombre de copies possibles : {max_h} x {max_v}")
        # quit()
        #taille déjà à jour
    
    if context.cols > 0:
        if context.cols > max_h:
            print(f"Warning : nombre de colonnes demandées ({context.cols}) > max calculé ({max_h})")
            copies_h = max_h
        else:
            copies_h = context.cols
 
        print(f"Nombre maximal de colonnes ajusté à {copies_h}")

    if context.rows > 0:
        if context.rows > max_v:
            print(f"Warning : nombre de lignes demandées ({context.rows}) > max calculé ({max_v})")
            copies_v = max_v
        else:
            copies_v = context.rows
        print(f"Nombre maximal de lignes ajusté à {copies_v}")

    #debug 

    # print("Nombre max :" , max_h, max_v)
    # print("Demandé par l'utilisateur :", context.cols, context.rows)
    # print("Valeur finale :", copies_h, copies_v)

    return copies_h, copies_v
