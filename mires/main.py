#!/usr/bin/env python3

import sys
import tifffile
import os.path

import argparse
import logging
from pathlib import Path

import numpy as np
from PIL import Image ,ImageDraw, ImageFont, ImageOps

from images_utils import load_image, get_dpi, trim_image, add_border
from layout_utils import compute_lens_width, compute_max_copies


def Set_tiff_voxel_size(file_path, ResX, ResY):
    """
    Implemented based on information found in https://pypi.org/project/tifffile
    """

    def _xy_voxel_size(tags, key):
        assert key in ['XResolution', 'YResolution']
        if key in tags:
            num_pixels, units = tags[key].value
            return units / num_pixels
        # return default
        return 1.

    with tifffile.TiffFile(file_path, mode="r+b") as tiff:
        
        # image = imread(file_path)
        image_metadata = tiff.imagej_metadata
        
        if image_metadata is not None:
            z = image_metadata.get('spacing', 1.)
        else:
            # default voxel size
            z = 1.

        tags = tiff.pages[0].tags

        tagYR = tags['YResolution']
        tagXR = tags['XResolution']

        print("Trouvé : ", tagXR.value[0], tagYR.value[0], tagYR.value[1])

        resUnit = int(tagYR.value[1])
        YR0 = ResY*resUnit
        XR0 = ResX*resUnit
        
        print("Nouvelles valeurs :", XR0, YR0, resUnit)

        tagYR.overwrite((YR0,resUnit))
        tagXR.overwrite((XR0,resUnit))
        

        # parse X, Y resolution

        y = _xy_voxel_size(tags, 'YResolution')
        x = _xy_voxel_size(tags, 'XResolution')
        
        #print (x)
        #print (y)
        
        # return voxel size
        return [z, y, x]


def run(args):
    
    #print(args.mire, args.image, args.LPI, args.HDPI, args.VDPI, args.tile)    
    print()
    
    #Leve la limite sur la taille des fichiers images
    #Il faudra voir jusqu'où aller
    
    Image.MAX_IMAGE_PIXELS = 2052314995

    # On charge la mire pour connaître les DPI
    
    try:
        TmpImage1 = Image.open(args.mire,"r")
        
        Hdpi = TmpImage1.info.get('dpi', (args.HDPI, args.VDPI))[0]
        Vdpi = TmpImage1.info.get('dpi', (args.HDPI, args.VDPI))[1]


        '''
        Pour l'impression
        DPI horizontal	TmpImage1.info.get('dpi')[0] ou --HDPI	720
        DPI vertical	TmpImage1.info.get('dpi')[1] ou --VDPI	360
        '''
        
    except IOError:
        print("Fichier mire non trouvé")
        quit()

    # On écrase les résolutions horizontales et verticales si renseignées

    if args.HDPI >= 0:
        Hdpi = args.HDPI
        
    if args.VDPI >= 0:
        Vdpi = args.VDPI
        
    print("Densité de points (DPI)", Hdpi, Vdpi)

    LensWidthInPixels = Hdpi/args.LPI #nombre réel ie pas un entier

    print("Largeur d'une lentille en pixels :",LensWidthInPixels)
        
    # Calcul initial du nom de fichier de sortie
    # Pour cela on détermine le nombre de lignes et colonnes

    CopiesH = args.cols
    CopiesV = args.rows
    
    if (args.cols == 0 or args.rows == 0) and str(args.image) != "Image_centree.tif":
        try:
            # On charge temporairement la mire et le fichier image
            # pour récupérer leurs caractéristiques
            # Ensuite, on les referme            
            #print(args.mire,args.image)
                        
            if args.makeshift <= 0:
                # On ne fait pas une mire de callage
                
                TmpImage2 = Image.open(args.image,"r")

                # Si on enlève les bords de l'image2, alors on recalcule sa taille
                # Vaudra zéro si on n'enlève rien                
                TrimValueH = args.trim/25.4*(TmpImage1.info.get('dpi', (args.HDPI, args.VDPI))[0])
                TrimValueV = args.trim/25.4*(TmpImage1.info.get('dpi', (args.HDPI, args.VDPI))[1])
                
                if args.cols <= 0:
                    CopiesH = int(TmpImage1.size[0]/(TmpImage2.size[0]-TrimValueH))
                else:
                    CopiesH = args.cols
                    
                if args.rows <= 0:    
                    CopiesV = int(TmpImage1.size[1]/(TmpImage2.size[1]-TrimValueV))
                else:
                    CopiesV = args.rows
                    
                TmpImage2.close
            else:
                # Pour créer une mire de callage
                CopiesH = args.makeshift
                CopiesV = int(LensWidthInPixels)
        except IOError:
            print("Fichier image ou mire non trouvées")
            quit()

    # On ferme le fichier mire
    TmpImage1.close

    #
    # Calcul du nom du fichier de sortie
    #
    
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
    # Dans ce cernieer cas, output est déjà ouvert
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
    # aors on ouvre celui là plutôt que args.image
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
        PixelsH = int(Hdpi*args.trim/25.4) # convertit les mm en pixels
        PixelsV = int(Vdpi*args.trim/25.4)
        print("Trimming", PixelsH,PixelsV,"pixels")
        
        img2 = img2.crop((PixelsH, PixelsV,a2-PixelsH, b2-PixelsV))
        a2, b2 = img2.size
        print("taille de l'image réduite en pixels",a2,b2)


    # Si on veut ajouter un bord [noir] aux images 
    
    if args.border >0 and args.makeshift <= 0:
        PixelsH = int(Hdpi*args.border/25.4) # convertit les mm en pixels
        PixelsV = int(Vdpi*args.border/25.4)
        print("Adding border of", PixelsH,PixelsV,"pixels")

        img2 = ImageOps.expand(img2, border=(PixelsH, PixelsV), fill=(0,0,0))
        
        a2, b2 = img2.size
        print("taille de l'image avec bordure en pixels",a2,b2)
        


    #Combien d'exemplaires ?
    # On divise la largeur de la mire par celle de l'image + 1 lentille

    if args.makeshift <= 0:
        MaxCopiesH = int(a1/(a2+int(LensWidthInPixels)+1)) # On se réserve une lentille de marge pour ajuster
        MaxCopiesV = int(b1/b2)
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
    # C'est le nimbre maximal - la position de départ
    
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
    # img1.save(args.output,dpi=(Hdpi,Vdpi),resolution_unit=2,compression="tiff_lzw")
    # Attention : les fichiers Tiff générés par Python ne fonctionnent pas bien
    # Pour cela, j'ai basculé sur un format PNG qui ne déteriore pas l'image
    # Ne pas utiliser de Jpeg
    # On peut changer cela en précisant le nom du fichier de sortie
    
    print("On tente d'écrire le fichier", OutputFileName)
    img1.save(OutputFileName,dpi=(Hdpi,Vdpi))

    #Set_tiff_voxel_size(args.output, Hdpi, Vdpi)


def main():
    """Assemblage et alignement images sur une mire centrée"""
    parser = argparse.ArgumentParser(
        description="Assemblage et alignement images sur une mire centrée."
    )
    parser.add_argument(
        "-m", 
        "--mire", 
        type=Path, 
        default="Mire 50 LPI 711x508.tif",
        help="Nom du fichier Frame"
    )
    parser.add_argument(
        "-i",
        "--image",
        type=Path,
        default="Image_centree.tif",
        help="Nom du fichier à insérer."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default="Non renseigné",
        help="Nom du fichier à créer. \nCalcule automatiquement un nom si non renseigné"
    )
    parser.add_argument(
        "-a",
        "--addfile",
        type=Path,
        default="Non renseigné",
        help="Nom du fichier à ajouter"
    )
    parser.add_argument(
        "--LPI",
        type=float,
        default=40.0,
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
    run(parser.parse_args())


if __name__ == "__main__":
    main()
