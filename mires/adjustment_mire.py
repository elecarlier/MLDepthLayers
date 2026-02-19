from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def crop_central_slice(mire, hdpi: int, lens_px: int):
    """Découpe le morceau central de 3 cm de large pour la mire."""
    
    width, height = mire.size

    slice_width = int(3 / 2.54 * hdpi) #on récuère un bout de la mire centrale (3cm)

    slice_height = int(height / (lens_px + 1)) #hauteur en fct de px -> on fait autant de copies décalées de 1px chacune

    crop = mire.crop((
        int(width/2 - slice_width/2), 0,
        int(width/2 + slice_width/2), slice_height
    ))
    #ancien code: crop-img2 a2-slice_width b2-slice_height
    return crop, slice_width, slice_height

def compute_column_shift(col_index, CopiesH, slice_width, width, lens_px):

    """Calcule le décalage vertical pour aligner la colonne.
    width : mire
    slice_width : morceau
    """

    #MilieuCible = int(a1 * ((2*H+1)/(2*CopiesH)))
    #aDebutCible = int(MilieuCible-a2/2)

    col_mid = int(width * ((2*col_index + 1) / (2 * CopiesH)))

    a_start = int(col_mid - slice_width/2 )

    centre_mire_h = width // 2

    delta = centre_mire_h - col_mid #ecart milieu

    lentilles_ecart = int(delta / lens_px)

    shift = int(delta - lentilles_ecart * lens_px)

    if shift < 0:
        shift += lens_px
    
    print("Le décalage calculé pour la colonne",col_index+1,"est de",shift)
    return  a_start, shift

def paste_column(context,mire, slice_img, copies_v, a_start, shift):
    """Colle les copies verticales et ajoute les numéros de lignes."""
    mire_width, mire_height = mire.size #a1 b1
    slice_width, slice_height = slice_img.size #a2 b2

    font = ImageFont.truetype("Arial Unicode.ttf", int(context.hdpi/5))
    font_no_shift = ImageFont.truetype("Arial Unicode.ttf", int(context.hdpi/3))
    draw = ImageDraw.Draw(mire)

    for V in range(copies_v):

        b_start = int(mire_height * ((2*(V + context.vpos -1) + 1)/(2*copies_v)) - slice_height/2)

        mire.paste(slice_img, (a_start + V, b_start))

        txt_font = font_no_shift if V == shift else font
        txt_color = "red" if V == shift else "black"
        draw.text((a_start + slice_img.width + int(context.hdpi/4), b_start),
                  str(V), font=txt_font, fill=txt_color)


def generate_output_name(args, context, mire, slice_img):
    mire_width, mire_height = mire.size #a1 b1
    slice_width, slice_height = slice_img.size #a2 b2


    input_name = Path(args.image).stem
    SizeH = int(mire_width / context.hdpi * 25.4)
    SizeV = int(mire_height / context.vdpi * 25.4)
    ExtensionTxt = " mire {ELPI} LPI {SIZEH}x{SIZEV} mm {ExeH} Ex @{DPIH}x{DPIV}.png"
    Extension = ExtensionTxt.format(ELPI=args.LPI,SIZEH=SizeH,SIZEV=SizeV,ExeH=args.makeshift,ExeV=int(context.lens_width_px), DPIH = int(context.hdpi), DPIV = int(context.vdpi ))               
    OutputFileName = input_name + Extension

    return OutputFileName


def create_alignment_mire(args,context, mire, output_path=None, erase=False):
    """Orchestre la création de la mire d'ajustement."""
    
    hdpi, vdpi = context.hdpi, context.vdpi
    lens_px = int(context.lens_width_px) # = CopiesV
    
    makeshift = context.makeshift
    vpos = context.vpos
    mire_width, mire_height = mire.size

    

    if erase:
        mire.paste((255, 255, 255), (0,0,mire.width,mire.height))


    slice_img, slice_width, slice_height = crop_central_slice(mire, hdpi, lens_px)
    #ancien code: crop-img2 a2-slice_width b2-slice_height

    MaxCopiesH = int(mire_width/(slice_width+int(lens_px+1)))

    if context.makeshift > MaxCopiesH:
            print("Trop de colonnes demandées")
            print("Le nombre maximal est de", MaxCopiesH)
            quit()

    CopiesH = context.makeshift
    middle_col = (CopiesH - 1) / 2

    for H in range(CopiesH):

        a_start, shift = compute_column_shift(H, CopiesH, slice_width, mire.width, lens_px)
        print(f"Décalage calculé pour la colonne {H+1}: {shift}")

        #Ne pas imprimer sur la colonne centrale (si impair) -> structurellement alignée sur la plaque + décallage 0 + perturbe la lecture de la mire centrale

        if H != middle_col:
            paste_column(context, mire, slice_img, lens_px,a_start, shift )

    if args.output == None:
        output_path = generate_output_name(args, context, mire, slice_img)
    else:
        output_path = args.output

    mire.save(output_path, dpi=(hdpi, vdpi))
    print("Fichier de sortie :", output_path)
    return output_path
