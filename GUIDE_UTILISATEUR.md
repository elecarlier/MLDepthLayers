# Guide d'utilisation — MLDepthLayers

**Auteure : Eléonore Carlier**

Ce guide est destiné aux personnes qui ne sont pas familières avec la programmation ou GitHub. Il explique pas à pas comment installer et utiliser ce projet.

---

## C'est quoi ce projet ?

Ce projet est un outil pour la **photographie lenticulaire**. La photographie lenticulaire, c'est une technique qui crée des images en 3D ou en mouvement — vous connaissez peut-être ces cartes postales ou autocollants qui changent d'image quand on les incline.

Pour créer ce genre d'image, il faut savoir "à quelle profondeur" se trouve chaque élément de la photo. C'est ce qu'on appelle une **carte de profondeur** : une image en niveaux de gris où les zones claires sont proches et les zones sombres sont loin (ou l'inverse).

Ce projet automatise la génération de ces cartes de profondeur à partir d'un fichier Photoshop (`.psd`) découpé en calques.

### Ce que fait le programme, étape par étape

1. Il ouvre votre fichier PSD et extrait chaque calque (layer) en image PNG séparée
2. Il crée un masque pour chaque calque (une silhouette en noir et blanc)
3. Il passe chaque image dans un modèle d'intelligence artificielle (Apple ML Depth Pro) qui génère une carte de profondeur
4. Il applique le masque sur la carte de profondeur pour isoler chaque calque
5. Il range les résultats dans des dossiers bien organisés à côté de votre fichier PSD

---

## Prérequis

### De quoi avez-vous besoin ?

- Un **Mac** (le projet a été développé et testé sur macOS)
- Un fichier **PSD** avec des calques séparés
- **Anaconda** (un gestionnaire d'environnements Python) — voir installation ci-dessous
- Une connexion internet pour télécharger le modèle d'IA (~2 Go)

### Anaconda est-il déjà installé ?

Ouvrez un terminal (cherchez "Terminal" dans Spotlight avec Cmd+Espace) et tapez :

```bash
conda --version
```

- Si une version s'affiche (ex. `conda 25.1.1`) → ✅ déjà installé, passez à l'étape suivante
- Sinon → installez Anaconda (voir ci-dessous)

### Installer Anaconda (si nécessaire)

Rendez-vous sur le site officiel d'Anaconda :

👉 https://www.anaconda.com/docs/getting-started/anaconda/install#macos-command-line-installer

Ou directement depuis le terminal :

```bash
curl -O https://repo.anaconda.com/archive/Anaconda3-2024.10-1-MacOSX-arm64.sh
bash Anaconda3-2024.10-1-MacOSX-arm64.sh
```

> **Note :** Le nom du fichier change avec les versions. Adaptez si nécessaire, ou téléchargez directement depuis le site.

Pendant l'installation, suivez les instructions à l'écran :
- Appuyez sur **Entrée** pour lire les conditions d'utilisation
- Tapez `yes` pour accepter
- Appuyez sur **Entrée** pour accepter le dossier d'installation par défaut
- Tapez `yes` pour initialiser conda automatiquement (recommandé)

Une fois terminé, **fermez et rouvrez le terminal**, puis vérifiez :

```bash
conda --version
```

Si une version s'affiche → ✅ installation réussie

---

## Récupérer le projet

### Option A — Avec un compte GitHub (recommandé)

Dans le terminal :

```bash
git clone https://github.com/elecarlier/MLDepthLayers
cd MLDepthLayers
```

### Option B — Sans compte GitHub

1. Sur la page GitHub du projet, cliquez sur le bouton vert **`<> Code`**
2. Sélectionnez **Download ZIP**
3. Décompressez l'archive dans le dossier de votre choix
4. Ouvrez le terminal et naviguez jusqu'au dossier décompressé :

```bash
cd chemin/vers/MLDepthLayers
```

---

## Installation

Cette étape ne se fait **qu'une seule fois**.

### Étape 1 — Créer l'environnement Python

Placez-vous dans le dossier `ml-depth-pro` à l'intérieur du projet :

```bash
cd ml-depth-pro
```

Créez l'environnement Conda avec toutes les dépendances :

```bash
conda env create -f environment.yml
```

> Cette commande peut prendre quelques minutes selon votre connexion internet.

Activez l'environnement :

```bash
conda activate ml-depth-pro
```

> Vous verrez `(ml-depth-pro)` apparaître au début de votre ligne de commande. C'est normal, ça signifie que l'environnement est actif.

Installez le package Python du modèle :

```bash
pip install -e .
```

Vérification :

```bash
python -c "import depth_pro; print(depth_pro.__name__)"
```

Si `depth_pro` s'affiche → ✅ tout est OK

> En cas d'erreur `No module named depth_pro`, réessayez : `conda activate ml-depth-pro`, puis `pip install -e .`

### Étape 2 — Télécharger le modèle d'IA

Toujours dans le dossier `ml-depth-pro/`, lancez :

```bash
source get_pretrained_models.sh
```

Le fichier `depth_pro.pt` (~2 Go) sera téléchargé dans le dossier `checkpoints/`.

**Si le script ne fonctionne pas**, téléchargez le fichier manuellement :

1. Ouvrez ce lien dans votre navigateur :
   `https://ml-site.cdn-apple.com/models/depth-pro/depth_pro.pt`
2. Placez le fichier téléchargé dans `ml-depth-pro/checkpoints/`

Vérification :

```bash
ls checkpoints/
```

Vous devriez voir `depth_pro.pt` → ✅

### Étape 3 — Revenir à la racine du projet

```bash
cd ..
```

Vous êtes maintenant à la racine de `MLDepthLayers/`, prêt à utiliser le projet.

---

## Utilisation

### Commande de base

```bash
python launcher.py chemin/vers/votre_fichier.psd
```

Remplacez `chemin/vers/votre_fichier.psd` par le chemin réel vers votre fichier Photoshop.

**Exemple :**

```bash
python launcher.py /Users/eleonore/Photos/portrait_lenticulaire.psd
```

### Options disponibles

| Option | Effet |
|--------|-------|
| `-v` ou `--verbose` | Affiche les détails de chaque étape pendant l'exécution |
| `-s` ou `--side` | Génère une image combinée (photo originale + carte de profondeur côte à côte) |
| `-c` ou `--cleanup` | Vide les dossiers temporaires avant de commencer |

**Exemples :**

```bash
# Avec logs détaillés et image côte à côte
python launcher.py -v -s chemin/vers/fichier.psd

# Tout réinitialiser avant de traiter un nouveau fichier
python launcher.py -c chemin/vers/fichier.psd
```

> **Important :** L'environnement `ml-depth-pro` doit être actif avant de lancer le programme. Si vous avez fermé le terminal depuis l'installation, relancez :
> ```bash
> conda activate ml-depth-pro
> ```

---

## Résultats

Une fois le programme terminé, deux nouveaux dossiers apparaissent **dans le même dossier que votre fichier PSD** :

```
dossier_de_votre_psd/
├── votre_fichier.psd
├── global_map/          ← masques appliqués sur la carte de profondeur globale
└── layers_map/          ← cartes de profondeur calculées calque par calque
```

Ces deux dossiers contiennent chacun une image par calque, avec fond transparent. Mais leur contenu est différent — et c'est là tout l'intérêt :

- **`layers_map/`** — Le modèle d'IA a traité **chaque calque séparément**, en ne voyant que l'élément découpé. La profondeur est donc calculée en fonction de l'élément isolé lui-même.

- **`global_map/`** — Le modèle d'IA a d'abord traité **l'image complète** (tous calques ensemble), puis les silhouettes de chaque calque ont été appliquées sur cette carte globale pour en extraire la portion correspondante. La profondeur reflète ici la place de chaque élément dans la scène entière.

Les deux approches donnent des résultats légèrement différents : `layers_map` tend à accentuer la profondeur propre à chaque objet, tandis que `global_map` préserve les relations de profondeur entre les éléments de la scène. Vous pouvez essayer les deux et choisir ce qui convient le mieux à votre rendu lenticulaire.

---

## Nettoyer les fichiers temporaires

Le programme crée des dossiers `input/` et `output/` temporaires dans le dossier du projet. Pour les vider :

```bash
python cleanup.py
```

Vous pouvez aussi ajouter `-c` à votre commande de lancement pour que le nettoyage se fasse automatiquement avant chaque exécution.

---

## En cas de problème

| Problème | Solution |
|----------|----------|
| `conda: command not found` | Fermez et rouvrez le terminal après avoir installé Anaconda |
| `No module named depth_pro` | Lancez `conda activate ml-depth-pro`, puis `pip install -e .` depuis `ml-depth-pro/` |
| `Fichier introuvable` | Vérifiez que le chemin vers votre PSD est correct et que l'extension est bien `.psd` |
| `Aucun layer extrait du PSD` | Vérifiez que vos calques sont bien visibles (non masqués) dans Photoshop |
| Le programme est très lent | C'est normal — le modèle d'IA traite chaque calque séparément, comptez quelques minutes par calque |
