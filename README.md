# lenticular_photgraphy

1) Install Anaconda
   
macOS Command Line installer: 
https://www.anaconda.com/docs/getting-started/anaconda/install#macos-command-line-installer

Suivre le tutoriel (vérifier avec l'index  	SHA256 présent ici : https://repo.anaconda.com/archive/) à l'époque (fev 2026)
curl -O https://repo.anaconda.com/archive/Anaconda3-2025.12-2-MacOSX-arm64.sh
bash ~/Anaconda3-2025.12-2-MacOSX-arm64.sh

Dans un terminal : 
 bash ~/Downloads/Anaconda3-2025.12-2-MacOSX-arm64.sh
 Press Return to continue. You can review Anaconda’s Terms of Service (TOS) at https://anaconda.com/legal.
Enter yes to agree to the TOS.
Press Return to accept the default install location (PREFIX=/Users/<USER>/anaconda3), or enter another file path to specify an alternate installation directory. The installation might take a few minutes to complete.
Choose an initialization options:

    Yes (Recommended) - conda modifies your shell configuration to initialize conda whenever you open a new shell and to recognize conda commands automatically.
    No - conda will not modify your shell scripts. After installation, if you want to initialize, you must do so manually. For more information, see Manual shell initialization.

The installer finishes and displays, “Thank you for installing Anaconda3!”

Close and re-open your terminal window for the installation to fully take effect,


vérifier l'instalation en fermant et ouvrant un second terminal : conda --version
si conda 25.11.1 -> ok 



2) Utilisation de ml-deph-pro

Il faut avoir installé Anaconda/miniconda au préalable (voir étape 1)
- Préparer un environnment python isolé
conda create -n depth-pro python=3.10
conda activate depth-pro

Ml-Depth-Pro-Env.yaml est l’environnement Conda.

pyproject.toml est pour le package Python.

get_pretrained_models.sh télécharge les modèles.


- Installer les dépendances 


# 2. Créer l'environnement conda
conda env create -f environment.yml

# 3. Activer l'environnement
conda activate ml-depth-pro


Depuis la racine du projet ml-Depth-Pro/, tape :

pip install -e .

il va installer le package défini par le pyproject.toml

Vérification: Après l’installation :

python -c "import depth_pro; print(depth_pro.__name__)"


Si ça imprime depth_pro → ✅ tout est OK

Télécharger le modèle pré-entrainé :


sh get_pretrained_models.sh

 Télécharger le checkpoint manuellement via le repo d'origin Apple

mkdir -p checkpoints


Vérification : 


Ensuite tu peux lancer le script principal en remplacant évidement par les bonnes valeurs:


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