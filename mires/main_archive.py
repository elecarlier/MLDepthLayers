#!/usr/bin/env python3

import sys
import tifffile
import os.path

import argparse
import logging
from pathlib import Path

import numpy as np
from PIL import Image ,ImageDraw, ImageFont, ImageOps
from mires_utils import calculate_copies
from parser import parse_args
from images_utils import (
    load_image,
    trim_image,
    load_and_prepare_image,
    get_dpi,
    add_border,
    compute_copies,
    paste_images,
    resolve_dpi,
)
from layout_utils import compute_lens_width, compute_max_copies


def run(args):
    
    #Leve la limite sur la taille des fichiers images
    Image.MAX_IMAGE_PIXELS = 2052314995

    # Chargement de la mire pour connaitre dpi (@ comment la mire peut nous donner la dpi ? )
    try:
        mire_img = load_image(args.mire)
    except FileNotFoundError:
        print(f"Mire {args.mire} non trouvée")
        sys.exit(1)

    hdpi, vdpi = resolve_dpi(mire_img, args.HDPI, args.VDPI)
    print("DPI:", hdpi, vdpi)


    #@ on renseignera surement les dpi (-> i guess pour l'imprimante??)
    LensWidthInPixels = hdpi/args.LPI #nombre réel ie pas un entier

    print("Largeur d'une lentille en pixels :",LensWidthInPixels)
        
    # Calcul initial du nom de fichier de sortie

    # Pour cela on détermine le nombre de lignes et colonnes
    
    #Valeur forcée
    # CopiesH = args.cols
    # CopiesV = args.rows
    
    #@? c'est quoi image_centre
    

    # if (args.cols == 0 or args.rows == 0) and str(args.image) != "Image_centree.tif":
    #     try:
    #         # On charge temporairement la mire et le fichier image
    #         # pour récupérer leurs caractéristiques
    #         # Ensuite, on les referme            
    #         #print(args.mire,args.image)
                        
    #         if args.makeshift <= 0:
    #             # On ne fait pas une mire de callage
                
    #             TmpImage2 = Image.open(args.image,"r")

    #             # Si on enlève les bords de l'image2, alors on recalcule sa taille
    #             # Vaudra zéro si on n'enlève rien                
    #             TrimValueH = args.trim/25.4*(TmpImage1.info.get('dpi', (args.HDPI, args.VDPI))[0])
    #             TrimValueV = args.trim/25.4*(TmpImage1.info.get('dpi', (args.HDPI, args.VDPI))[1])
                
    #             if args.cols <= 0:
    #                 CopiesH = int(TmpImage1.size[0]/(TmpImage2.size[0]-TrimValueH))
    #             else:
    #                 CopiesH = args.cols
                    
    #             if args.rows <= 0:    
    #                 CopiesV = int(TmpImage1.size[1]/(TmpImage2.size[1]-TrimValueV))
    #             else:
    #                 CopiesV = args.rows
                    
    #             TmpImage2.close
    #         else:
    #             # Pour créer une mire de callage
    #             CopiesH = args.makeshift
    #             CopiesV = int(LensWidthInPixels)
    #     except IOError:
    #         print("Fichier image ou mire non trouvées")
    #         quit()

    # # # On ferme le fichier mire
    # # TmpImage1.close
    
    CopiesH, CopiesV = calculate_copies(args.mire, args.image, args)
    print("Colonnes calculées :", CopiesH, "Lignes calculées :", CopiesV)
    # Calcul du nom du fichier de sortie
    
    
    if str(args.output) != "Non renseigné":
        # Le fichier de sortie est renseigné
        # On va utiliser cette valeur
        
        OutputFileName = str(args.output)
    else:
       # On calcule un nom de fichier
        
       name = Path(args.image).stem
       
       #Si on assemble des images
       if args.makeshift <= 0:
           ExtensionTxt = " {ExeH}x{ExeV}.png"
           Extension = ExtensionTxt.format(ELPI=args.LPI,ExeH=CopiesH,ExeV=CopiesV)
       #Si on crée une mire de callage
       else:
           ExtensionTxt = " mire {ELPI} {ExeH}x{ExeV}.png"
           Extension = ExtensionTxt.format(ELPI=args.LPI,ExeH=args.makeshift,ExeV=int(LensWidthInPixels))
           
       OutputFileName = name + Extension

    print("Le fichier de sortie :", OutputFileName)

    # Si args.add == false et args.addfile == "Non renseigné", on charge la mire normalement
    # sinon, on charge le fichier output s'il existe déjà
    # S'il n'existe pas, on charge la mire

    #print("addfile '", args.addfile,"'", str(args.addfile) == "Non renseigné")
    
    if args.add or str(args.addfile) != "Non renseigné" :
        
        # On teste si le fichier output existe déjà
        # S'il existe on l'ouvre en mode écriture
        
        #print("On veut ajouter au fichier", OutputFileName)
        try:
            img1 = Image.open(OutputFileName)
            NomFichierMire = OutputFileName
            print("Le fichier de sortie existe déjà. On y ajoute les images")
        except IOError:
            print("Le fichier de sortie n'existe pas encore. On va débuter avec la mire")
            NomFichierMire = str(args.mire)
            
    else:
        print("On crée à partir du fichier mire")
        NomFichierMire = str(args.mire)
    
    # Opening the primary image (used in background)

    #
    # On ouvre le fichier mire sauf si on ajoute à output
    # Dans ce dernier cas, output est déjà ouvert
    #
    
    #print("NomFichierMire", NomFichierMire)
    if NomFichierMire == str(args.mire):
        try:
           img1 = Image.open(NomFichierMire,mode="r")
        except IOError:
           print("Mire",NomFichierMire,"non trouvée")
           quit()

    # n calcule les tailles des images en pixels

    '''
    Largeur de la mire	TmpImage1.size[0]	17280 px
    Hauteur de la mire	TmpImage1.size[1]	8055 px
    '''
    a1, b1 = img1.size
    print("Taille de la mire en px", a1,b1)
    

    #
    # Opening the secondary image (overlay image)
    #
    
    # SI on ajoute une image par --addfile
    # alors on ouvre celui là plutôt que args.image
    # Dans ce cas, renseigner --cols et --row car sinon le positionnement peut être imprévisible

    if str(args.addfile) != "Non renseigné":
        NomFichierImage = str(args.addfile)
    else:
        NomFichierImage = str(args.image)

    # On lit le fichier sauf si --makeshift est renseigné
    # car alors on ne l'utilisera pas
    
    if args.makeshift <= 0:
        try:
            img2 = Image.open(NomFichierImage, mode="r")
        except IOError:
            print("Image",NomFichierImage,"non trouvée")
            quit()

        a2, b2 = img2.size
        print("taille image",a2,b2)

    #Enlever les bords d'alignement de img2 si Trim >0
    # On attend des valeurs en milimètres (mm)
    
    if args.trim > 0 and args.makeshift <= 0:
        '''
        PixelsH = int(Hdpi*args.trim/25.4) # convertit les mm en pixels
        PixelsV = int(Vdpi*args.trim/25.4)
        print("Trimming", PixelsH,PixelsV,"pixels")
        img2 = img2.crop((PixelsH, PixelsV,a2-PixelsH, b2-PixelsV))
        '''
        img2 = trim_image(img2, args.trim, hdpi, vdpi)



        a2, b2 = img2.size
        print("taille de l'image réduite en pixels",a2,b2)


    # Si on veut ajouter un bord [noir] aux images 
    
    if args.border >0 and args.makeshift <= 0:
        '''
        PixelsH = int(Hdpi*args.border/25.4) # convertit les mm en pixels
        PixelsV = int(Vdpi*args.border/25.4)
        print("Adding border of", PixelsH,PixelsV,"pixels")
    

        img2 = ImageOps.expand(img2, border=(PixelsH, PixelsV), fill=(0,0,0))
        '''
        img2 = add_border(img2, args.border, hdpi, vdpi)
        a2, b2 = img2.size
        print("taille de l'image avec bordure en pixels",a2,b2)
        


    #Combien d'exemplaires ?
    # On divise la largeur de la mire par celle de l'image + 1 lentille

    if args.makeshift <= 0:
        LensWidthInPixels = compute_lens_width(hdpi, args.LPI)
        MaxCopiesH, MaxCopiesV = compute_max_copies(img1.size, img2.size, LensWidthInPixels)
    else:
        # Si on crée une mire de callage, alors le nombre de colonnes
        # est égal à l'argument passé dans makeshift
        MaxCopiesH = args.makeshift
        MaxCopiesV = int(LensWidthInPixels)
        

    #SI on veut seulement savoir combien de copies rentrent
    if args.test:
        print("Nombre de copies possibles",MaxCopiesH,"par",MaxCopiesV)
        quit()

    #Si on a forcé le nomre de lignes ou de colonnes
    if args.cols > 0:
        if args.cols>MaxCopiesH:
            print("Warning : nombre de colonnes demandées supérieur au nombre maximal calculé",MaxCopiesH)
        MaxCopiesH = args.cols
        print("Nombre maximal de colonnes ajusté à", MaxCopiesH)
        
    if args.rows > 0:
        if args.rows>MaxCopiesV:
            print("Warning : nombre de lignes demandées supérieur au nombre maximal calculé",MaxCopiesV)
        MaxCopiesV = args.rows
        print("Nombre maximal de lignes ajusté à", MaxCopiesV)

    # Si on a demandé de remplir la mire avec des copies de image
    # On calcule combien il estt possible d'en créer
    # C'est le nombre maximal - la position de départ
    
    if args.tile: 
        CopiesH = MaxCopiesH-args.HPos+1
        CopiesV = MaxCopiesV-args.VPos+1
    else:
        CopiesH = 1
        CopiesV = 1

    # Si on a renseigné des nombres d'exemplaires

    if args.HCopies != -1:
        
        if args.HCopies < 0:
            print("Le nombre de copies horizontales doit être positif")
            quit()
        else:
            CopiesH = min(args.HCopies,MaxCopiesH-args.HPos+1)
        
    if args.VCopies != -1:
        if args.VCopies < 0:
            print("Le nombre de copies verticales doit être positif")
            quit()
        else:
            CopiesV = min(args.VCopies,MaxCopiesV-args.VPos+1)    
            
    print("Nombre de copies :",CopiesH,"horizontales", CopiesV, "verticales")
    print("")

    # Si shiftlist est renseigné
    # On vérifie que les valeurs de décalages sont en nombre suffisant
    # Il faut une valeur par colonne (de 0 à MaxCopies-1)
    # même si on ne les utilise pas toutes
    # Cela permet d'avoir toujours la même liste de valeurs si on combine
    # plusieurs fichier

    if args.shiftlist[0] != -1 and len(args.shiftlist) < MaxCopiesH:
        print("Trop peux de valeurs de position!")
        print("Il y a",MaxCopiesH,"colonnes et seulement",len(args.shiftlist),"valeurs renseignées")
        quit()
    elif args.shiftlist[0] != -1:
        for V in range(MaxCopiesH):
            print("Décalage forcé sur la colonne",V+1,"est de",args.shiftlist[V])

    #
    # CA Y EST, on commence à travailler
    # On recopie CopiesH x CopiesV fois l'image 2 dans l'image 1
    #

    LensMilieu = int(LensWidthInPixels/2)
    CentreMireH = int(a1/2)
    
    if args.makeshift <= 0:
        # C'est le cas de figure normal
        # On crée une image avec CopiesH x CopiesV exemplaires
        # de img2 dans img1        

        #Efface la mire si on le demande
        if args.erase and NomFichierMire == str(args.mire):
            print("Effacement de la mire - remplir en blanc")
            img1.paste((255,255,255),(0,0,a1,b1))

        print("On recopie les images")
        print("On va faire",CopiesH,"Colonnes","et",CopiesV,"lignes")
        
        for H in range(CopiesH):

            #print("H",H,"a1",a1,"MaxCOpiesH",MaxCopiesH,"args.HPos-1",args.HPos-1,"2*(H+args.HPos-1)+1",2*(H+args.HPos-1)+1,"2*MaxCopiesH",2*MaxCopiesH)
            MilieuCible = int(a1 * ((2*(H+args.HPos-1)+1)/(2*MaxCopiesH)))
            
            #print("H",H,"Milieu cible",MilieuCible)
            aDebutCible = int(MilieuCible-a2/2)            
            EcartMilieu = CentreMireH-MilieuCible           
            LentillesEcart = int(EcartMilieu/LensWidthInPixels)

            #De combien faut-il décaler pour que les centres soient alignés
            ShiftCible = int(EcartMilieu - LentillesEcart*LensWidthInPixels)

            # Si on a reçu des valeurs de décalage à appliquer
            # Le tableau args.shiftlist les contient par colonnes
            # de 0 à MaxCopiesH
            
            if args.shiftlist[0]!= -1:
                print("On a reçu des décalages à appliquer par colonne")
                print("Cette colonne est décalée de", args.shiftlist[H+args.HPos-1],"plutot que",ShiftCible)
                ShiftCible = args.shiftlist[H+args.HPos-1]               
            
            #print("cible",aDebutCible, "milieu", MilieuCible, "Ecart",EcartMilieu,"(",LentillesEcart,") Shift",ShiftCible)
            aDebut=aDebutCible + ShiftCible 
            
            #print("aDebut",aDebut, "Milieu", aDebut+int(a2/2), "delta",(CentreMireH-(aDebut+a2/2))/LensWidthInPixels,"Shift",ShiftCible)
            
            for V in range(CopiesV):
                bDebut = int(b1*((2*(V+args.VPos-1)+1)/(2*MaxCopiesV))-b2/2)
                img1.paste(img2, (aDebut,bDebut))
    else:
        # Si on a demandé de créer une mire d'ajustement des lentilles
        # On va crée autant de lignes qu'il y a de pixels par lentille
        # et y recopier le centre de la mire d'alignement
        # Il faudra repérer la ligne qui est parfaitement alignée
        # puis l'utliser l'indice en paramètre pour les impressions suivante
        
        # La valeur de makeshift indique le nombre de colonnes à créer
        
        print("On crée une mire d'ajustement")

        # On récupère un bout de la mire centrale de 3 cm de large
        
        SliceSizeH = int(3/2.54*Hdpi)
                         
        # La hauteur est en fonction du nombre de pixels par lentille
        # car on va en faire autant de copies décalées de 1 px chacunes
                         
        SliceSizeV = int(b1/(LensWidthInPixels+1))                         
        CopiesV = int(LensWidthInPixels)
       
        # On récupère un bout de la mire centrale
        img2=img1.crop((int(a1/2-SliceSizeH/2),0,int(a1/2+SliceSizeH/2),SliceSizeV))
        a2, b2 = img2.size

        #Efface la mire centrale si on le demande
        if args.erase :
            print("Effacement de la mire - remplir en blanc")
            img1.paste((255,255,255),(0,0,a1,b1))

        # On ajuste le nombre de colonnes pour ignorer la taille de input
        MaxCopiesH = int(a1/(a2+int(LensWidthInPixels+1)))

        if args.makeshift > MaxCopiesH:
            print("Trop de colonnes demandées")
            print("Le nombre maximal est de", MaxCopiesH)
            quit()
                         
        CopiesH = args.makeshift

        # Pour pouvoir écrire les numéros de lignes
        # On crée un objet draw et un objet font
        # On espère que "Arial Unicode.ttf" est présent sur l'ordinateur
                         
        draw = ImageDraw.Draw(img1)
        font = ImageFont.truetype("Arial Unicode.ttf",int(Hdpi/5))
        fontNoShift = ImageFont.truetype("Arial Unicode.ttf",int(Hdpi/3))

        ColonneDuMilieu = (CopiesH-1) /2        
        #print("Colonne du milieu",ColonneDuMilieu)
        
        for H in range(CopiesH):
            MilieuCible = int(a1 * ((2*H+1)/(2*CopiesH)))
            aDebutCible = int(MilieuCible-a2/2)            
            EcartMilieu = CentreMireH-MilieuCible           
            LentillesEcart = int(EcartMilieu/LensWidthInPixels)

            #De combien faut-il décaler pour que les centres soient alignés
            ShiftCible = int(EcartMilieu - LentillesEcart*LensWidthInPixels)
            if ShiftCible <0:
                ShiftCible = ShiftCible + int(LensWidthInPixels)            
            
            #print("cible",aDebutCible, "milieu", MilieuCible, "Ecart",EcartMilieu,"(",LentillesEcart,") Shift",ShiftCible)
            aDebut=aDebutCible
            
            #aDebut = aDebutCible+ShiftCible
            
            #print("On va faire", CopiesV,"copies")
            print("Le décalage calculé pour la colonne",H+1,"est de",ShiftCible)
            
            #print("aDebut",aDebut, "Milieu", aDebut+int(a2/2), "delta",(CentreMireH-(aDebut+a2/2))/LensWidthInPixels,"Shift",ShiftCible)

            #print("H",H,"ColonneDuMileu",ColonneDuMilieu)

            # On n'imprime pas sur la colonne centrale (en cas de nombre impair de colonnes)
            # Elle est structurellement alignée sur la plaque
            # Le décallage doit être 0 de toute façon
            # En plus, ca vient perturber la lecture de la mire centrale
            
            if H != ColonneDuMilieu:
                for V in range(CopiesV):
                    bDebut = int(b1*((2*(V+args.VPos-1)+1)/(2*CopiesV))-b2/2)
                    #print(aDebut-int((CopiesV/2-V)),bDebut)
                
                    img1.paste(img2, (aDebut+V,bDebut))
                    
                    # On écrit la ligne théorique calculée en rouge
                    # Sinon,en noir
                    if V == ShiftCible:                
                        draw.text((aDebut+SliceSizeH+int(Hdpi/4),bDebut),str(V),font=fontNoShift,fill="red")
                    else:
                        draw.text((aDebut+SliceSizeH+int(Hdpi/4),bDebut),str(V),font=font,fill="black")

        # On ajuste le nom du fichier de sortie
        
        if str(args.output) == "Non renseigné":            
           name = Path(args.image).stem
           SizeH = int(a1 / Hdpi * 25.4)
           SizeV = int(b1 / Vdpi * 25.4)
           #Si on assemble des images
           ExtensionTxt = " mire {ELPI} LPI {SIZEH}x{SIZEV} mm {ExeH} Ex @{DPIH}x{DPIV}.png"
           Extension = ExtensionTxt.format(ELPI=args.LPI,SIZEH=SizeH,SIZEV=SizeV,ExeH=args.makeshift,ExeV=int(LensWidthInPixels), DPIH = int(Hdpi), DPIV = int(Vdpi))               
           OutputFileName = name + Extension

        print("Le fichier de sortie :", OutputFileName)
                                        
    # Saving the image
    # On peut changer cela en précisant le nom du fichier de sortie
    
    print("On tente d'écrire le fichier", OutputFileName)
    img1.save(OutputFileName,dpi=(hdpi,vdpi))

def main():
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
