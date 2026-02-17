⚠️ **Attention : ce dépôt contient plusieurs licences.**

## 1. ML Depth Pro (Apple)

Dans le dossier `ml-depth-pro`, ce projet contient une version modifiée de **Apple ML Depth Pro**.  
- Copyright © 2024 Apple Inc., All Rights Reserved  
- Modifications apportées par **Eléonore Carlier**  

**Conditions légales :**  
- Le code Apple doit rester sous licence Apple, avec le copyright et le disclaimer intacts.  
- Ne pas utiliser le logo ou nom Apple pour promouvoir ce projet.  

## 2. Bibliothèques tierces

Ce projet utilise également plusieurs composants sous **Apache License 2.0** :  
- **timm** (PyTorch Image Models) – Ross Wightman  
- **DINOv2** – Facebook Research  

Pour les licences et notices complètes, voir [ACKNOWLEDGEMENTS.md](ml-depth-pro/ACKNOWLEDGEMENTS.md).  

## 3. Description générale

Ce dépôt regroupe plusieurs projets liés à la **photographie lenticulaire** et au traitement d’images.  
Il inclut notamment `ml-depth-pro`, utilisé pour générer des cartes de profondeur à partir d’images.



## 1. Récupérer le projet

Rendez-vous sur le dépôt GitHub :

👉 https://github.com/elecarlier/MLDepthLayers

### Option A — Vous avez un compte GitHub (recommandé)

Dans un terminal :

```bash
git clone https://github.com/elecarlier/MLDepthLayers
cd MLDepthLayers
```



### Option B — Sans compte GitHub

Cliquez sur le bouton vert <> Code
Sélectionnez Download ZIP
Décompressez l’archive dans le dossier de votre choix

## 2. Contenu du dépot
Vous venez de télécharger les fichiers sources.  
A l'intérieur, vous trouverez des dossiers différents:

ml-Deptth-Pro : création des cartes de profondeur
...:


Nous allons commencer par l'instalaion de ces différents projets.

## 3. Pré-requis

Pour le bon fonctionnement de ces différents projets, l'installation de Anaconda/miniconda est nécessaire. Si cela est déjà installé sur votre machine, vous pouvez skipper la première étape. 

Comment savoir si Anaconda est déjà installé? 

Tapez dans votre terminal:
```bash
conda --version
```
Si une version s’affiche (ex. conda 25.11.1) → ✅ déjà installé
Sinon → passez à l’étape suivante.


Lors de l'instalation des différents projets, nous devons nous trouver à la racine du projet en question.


Nous allons commencer par l'installation de ml-depth-pro.

## 4. Installation de ml-Depth-Pro

Ouvrez un terminal et rendez-vous dans la racine du dossier ml-depth-pro.


1) Installer Anaconda (macOS)

(Si déjà installé, rendez-vous directement à la deuxième étape)

Télécharger le Command Line Installer :

https://www.anaconda.com/docs/getting-started/anaconda/install#macos-command-line-installer

Vérifier le checksum SHA256 si nécessaire (https://repo.anaconda.com/archive/)


Dans un terminal : 

```bash
curl -O https://repo.anaconda.com/archive/Anaconda3-2025.12-2-MacOSX-arm64.sh
bash Anaconda3-2025.12-2-MacOSX-arm64.sh
```

Note: Le nom du fichier peut changer avec le temps.
Adaptez la commande si nécessaire.

L'installation démarre et des instructions apparaissent à l'écran, suivez les. 

Instructions pendant l’installation
    Appuyez sur Return pour continuer et lire les Terms of Service : TOS Anaconda

    Tapez yes pour accepter les termes.

    Appuyez sur Return pour accepter le chemin par défaut (/Users/<USER>/anaconda3) ou spécifiez un chemin alternatif.

    Choisissez une option d’initialisation :

        Yes (Recommended) : conda sera initialisé automatiquement dans votre shell.

        No : vous devrez initialiser conda manuellement après l’installation.

Une fois terminé, le message suivant apparaît :

    “Thank you for installing Anaconda3!”


Fermez et rouvrez le terminal pour que l’installation soit prise en compte.

Vérification de l'instalation 
```bash
conda --version
```

Si une version s’affiche → ✅ installation réussie


2) Installation de ml-deph-pro

Assurez-vous d’avoir installé Anaconda/miniconda (voir étape 1).

Placez-vous dans le dossier du projet 

a) Créer un environnement Python isolé

    conda create -n depth-pro python=3.10
    conda activate depth-pro

ml-depth-pro est un nom choisi, vous pouvez en utiliser un autre si besoin.

b) Installer les dépendances 

Toujours depuis la racine de ml-Depth-Pro/ :

```bash
# Créer l'environnement Conda
conda env create -f environment.yml

# Activer l'environnement
conda activate ml-depth-pro

# Installer le package Python défini par pyproject.toml
pip install -e .
```
Cela installe :

l’environnement Conda
les dépendances Python
le package depth_pro via pyproject.toml

Vérification: 
```bash
python -c "import depth_pro; print(depth_pro.__name__)"
```

Si cela affiche : depth_pro → ✅ tout est OK

Note : En cas d’erreur No module named depth_pro, vérifiez que l’environnement est bien activé : essayez de réactiver l'environnement avec
```bash
conda activate ml-depth-pro
```

c) Télécharger le modèle pré-entrainé 

Dans le terminal : 

sh get_pretrained_models.sh

Note : Si vous n’avez pas wget ou sudo, le script vous guidera pour télécharger le checkpoint manuellement depuis. 

Voici un duplicata des instructions :
Ouvre ce lien dans ton navigateur pour télécharger le modèle :
https://ml-site.cdn-apple.com/models/depth-pro/depth_pro.pt"
Place le fichier téléchargé dans le dossier : checkpoints/"


Vérification : 
```bash 
ls checkpoints/
```

Vous devriez voir un fichier depth_pro.pt

Vous pouvez ensuite lancer le projet avec la commande :

```bash
# Logs détaillés et side-by-side activé
python launcher.py -v -s path/to/PSD.psd

# Pipeline minimal
python launcher.py path/to/PSD.psd

avec path/to/PSD.psd comme étant le chemin vers votre image


Pour vider le contenu des dossiers input et output, veuillez utilisez le script prévu à cet effet:

```bash
python cleanup.py
```

## Documentation Complète

Pour une explication détaillée du pipeline, des options, et du flux des fichiers, consultez le fichier [documentation.md](ml-Depth-pro/documentation.md) dans ce dépôt.
