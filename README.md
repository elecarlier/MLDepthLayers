# lenticular_photgraphy


Ce dépôt regroupe plusieurs projets liés à la photographie lenticulaire.  
Il inclut notamment **ml-Depth-Pro**, utilisé pour générer des cartes de profondeur à partir d’images.

---

## 1. Récupérer le projet

Rendez-vous sur le dépôt GitHub :

👉 https://github.com/elecarlier/lenticular_photgraphy

### Option A — Vous avez un compte GitHub (recommandé)

Dans un terminal :

```bash
git clone https://github.com/elecarlier/lenticular_photgraphy.git
cd lenticular_photgraphy
```



### Option B — Sans compte GitHub

Cliquez sur le bouton vert <> Code
Sélectionnez Download ZIP
Décompressez l’archive dans le dossier de votre choix

## 2. Contenu du dépot
Vous venez de télécharger les fichiers sources.  
A l'intérieur, vous trouverez 3 dossiers différents:

ml-Deptth-Pro : création des cartes de profondeur
Midas-Master_3.1 :


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


L'installation est terminée. Vous pouvez lancer l’inférence sur une image avec le script run.py.

Exemple simple:

python run.py -i input/_U8A2060-Modifie.png -o Output/ -s


| Argument               | Usage                                               |
| ---------------------- | --------------------------------------------------- |
| `-i` / `--image-path`  | Chemin vers l’image ou le dossier d’images d’entrée |
| `-o` / `--output-path` | Dossier où sauver les résultats                     |
| `--skip-display`       | Ne pas afficher les images avec matplotlib          |
| `-v` / `--verbose`     | Afficher les logs                                   |
| `-s` / `--side`        | Générer des images côte-à-côte (RGB + profondeur)   |


Les images traitées sont dans Output/

Les fichiers *_map.jpg et *_lkg.jpg sont créés avec la profondeur estimée




```bibtex
@article{Bochkovskii2024:arxiv,
  author     = {Aleksei Bochkovskii and Ama\"{e}l Delaunoy and Hugo Germain and Marcel Santos and
               Yichao Zhou and Stephan R. Richter and Vladlen Koltun}
  title      = {Depth Pro: Sharp Monocular Metric Depth in Less Than a Second},
  journal    = {arXiv},
  year       = {2024},
  url        = {https://arxiv.org/abs/2410.02073},
}