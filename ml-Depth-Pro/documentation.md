# ML-Depth-Pro - Documentation

## Objectif
Ce projet génère des cartes de profondeur à partir d'un fichier PSD, isolant chaque layer et produisant des visualisations side-by-side optionnelles.

## Pipeline
1. Extraction des layers PSD → PNG
2. Génération des masques binaires
3. Génération des depth maps (cartes de profondeur)
4. Isolation des depth maps par layer
5. (Optionnel) Image side-by-side pour l'image globale
6. Export final des dossiers `global_map` et `layers_map`

## Options
| Option | Effet |
|--------|-------|
| `-v`, `--verbose` | Affiche tous les logs détaillés. |
| `-s`, `--side` | Génère une image combinée (side-by-side) pour l'image globale. |

## Détails du pipeline

### Étape 1 : Extraction PSD → PNG
- Fonction : `extract_layers(psd_path)`
- Sortie : `input/layers/0000_nomLayer.png`, etc.
- Dernier layer = **image globale**

### Étape 2 : Génération des masques
- Fonction : `generate_masks()`
- Sortie : `output/masks/000X_nomLayer_mask.png`

### Étape 3 : Génération des depth maps
- Fonction : `generate_depth_maps(image_paths)`
- Appelle `run.py` pour chaque layer PNG
- Sortie : `output/depth_maps_layers/000X_nomLayer_map.jpg`

### Étape 4 : Isolation des depth maps
- Fonction : `isolate_layers()`
- Sortie : `output/isolated_layers/000X_nomLayer_isolated.png`

### Étape 5 : (Optionnel) Side-by-side
- Fonction : `generate_side_by_side(global_image, final_folder)`
- Sortie : `<PSD_folder>/<PSD_nom>_lkg.jpg`

### Étape 6 : Export final
- Fonction : `export_results(psd_path)`
- Dossiers finaux :
  - `global_map/` → depth map globale
  - `layers_map/` → depth maps isolées par layer

## Flux des fichiers

PSD source
└─> input/layers/ (PNG layers)
└─> output/masks/ (masques binaires)
└─> output/depth_maps_layers/ (depth maps générées)
└─> output/isolated_layers/ (depth maps isolées)
└─> global_map/ & layers_map/ (export final)


## Utilisation
```bash
# Logs détaillés et side-by-side activé
python launcher.py -v -s path/to/PSD.psd

# Pipeline minimal
python launcher.py path/to/PSD.psd
