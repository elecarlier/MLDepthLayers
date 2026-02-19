from pathlib import Path

def compute_output_filename(args, context, copies_h, copies_v):
    """
    Génère automatiquement le nom du fichier output

    """
    #(cas simple : pas de --add, pas de --addfile, pas de --output)

    if args.output == None:
    # Nom du fichier input sans extension
        input_name = Path(args.image).stem

        # Taille de la mire
        #mire_w, mire_h = context.hdpi, context.vdpi
        mire_w, mire_h = context.mire_width, context.mire_height

        # LPI
        lpi = int(context.lpi)
        hdpi = context.hdpi
        vdpi = context.vdpi

        filename = f"{input_name} {mire_w}x{mire_h} @{hdpi}x{vdpi} {copies_h}x{copies_v} {lpi}LPI.png"
    else:
        filename = args.output

    # print("Nom du fichier output: ", filename)
    return filename

