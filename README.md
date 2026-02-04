# lenticular_photgraphy


Récuperer les projets. 


Rendez-vous sur ce lien : https://github.com/elecarlier/lenticular_photgraphy

Vous trouverez un bouton vert <> Code : appuyez dessus dessus et téléchargez le fichier zip


Vous venez de télécharger les fichiers sources de ml-deph-pro, ,,,, etc.

Unzip le et rentrer dans le dossier. 
Désormais nous nous trouvons à la racine des projets. Nous allons commencer par l'installation de ml-depth-pro.

Ouvrez un terminal et rendez-vous dans le dossier unzipper. (via cd etcc)



Installation de ml-Depth-Pro

1) Installer Anaconda (macOS)

Télécharger le Command Line Installer :

https://www.anaconda.com/docs/getting-started/anaconda/install#macos-command-line-installer

Vérifier le checksum SHA256 si nécessaire (https://repo.anaconda.com/archive/)


Dans un terminal : 
    curl -O https://repo.anaconda.com/archive/Anaconda3-2025.12-2-MacOSX-arm64.sh
 bash ~/Downloads/Anaconda3-2025.12-2-MacOSX-arm64.sh


Suivez les instructions à l’écran :

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
    conda --version

si conda 25.11.1 (ou similaire) -> ok 


2) Utilisation de ml-deph-pro

Assurez-vous d’avoir installé Anaconda/miniconda (voir étape 1).

a) Créer un environnement Python isolé

    conda create -n depth-pro python=3.10
    conda activate depth-pro


b) Installer les dépendances 

Depuis la racine du projet ml-Depth-Pro/ :

# Créer l'environnement Conda
conda env create -f environment.yml

# Activer l'environnement
conda activate ml-depth-pro

# Installer le package Python défini par pyproject.toml
pip install -e .


Vérification: 

python -c "import depth_pro; print(depth_pro.__name__)"

Si ça imprime depth_pro → ✅ tout est OK


c) Télécharger le modèle pré-entrainé 

sh get_pretrained_models.sh

Note : Si vous n’avez pas wget ou sudo, le script vous guidera pour télécharger le checkpoint manuellement depuis :
https://ml-site.cdn-apple.com/models/depth-pro/depth_pro.pt

et le placer dans le dossier checkpoints/

Vérification : ls checkpoints/

Vous devriez voir depth_pro.pt

L'installation est terminée. Vous pouvez lancer l’inférence sur une image avec le script run.py.

Exemple:

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

Tout est reproductible sur une machine vierge, sans sudo ni wget


```bibtex
@article{Bochkovskii2024:arxiv,
  author     = {Aleksei Bochkovskii and Ama\"{e}l Delaunoy and Hugo Germain and Marcel Santos and
               Yichao Zhou and Stephan R. Richter and Vladlen Koltun}
  title      = {Depth Pro: Sharp Monocular Metric Depth in Less Than a Second},
  journal    = {arXiv},
  year       = {2024},
  url        = {https://arxiv.org/abs/2410.02073},
}