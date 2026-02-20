# MLDepthLayers

A pipeline for **lenticular photography** that automatically generates per-layer depth maps from a layered Photoshop (PSD) file, using Apple's [ML Depth Pro](https://github.com/apple/ml-depth-pro) AI model.

**Created by Eléonore Carlier**

---

## What it does

Given a PSD file with multiple layers, the pipeline:

1. Extracts each layer as a PNG image
2. Generates a binary mask from each layer's alpha channel
3. Runs ML Depth Pro to produce a depth map for each layer
4. Isolates each depth map using its corresponding mask
5. Exports results into `global_map/` and `layers_map/` folders next to the original PSD

Optionally generates a side-by-side view (original + depth map) for Looking Glass displays.

---

## Documentation

- **Installation & usage guide (French):** [GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md)
- **Technical pipeline reference (English):** [TECHNICAL.md](TECHNICAL.md)

---

## Quick start (developers)

```bash
# 1. Set up the depth_pro model
cd ml-depth-pro
conda env create -f environment.yml
conda activate ml-depth-pro
pip install -e .
source get_pretrained_models.sh
cd ..

# 2. Run the pipeline
python launcher.py path/to/your/file.psd

# With options
python launcher.py -v -s -c path/to/your/file.psd
#   -v   verbose logging
#   -s   generate side-by-side image
#   -c   clean input/output folders before running
```

---

## Repository structure

```
MLDepthLayers/
├── launcher.py                 # Main entry point — start here
├── run.py                      # Depth Pro inference (modified from Apple's)
├── generate_masks.py           # Binary mask generation from layer alpha channels
├── generate_isolated_map.py    # Apply masks to depth maps
├── format_utils.py             # PSD extraction and file export utilities
├── dilate_image.py             # Scale/dilate depth map images
├── cleanup.py                  # Clean input/output folders
├── utils.py                    # Shared utility functions
├── display_tiff.py             # Utility: display TIFF pages
├── ToGrayScale.py              # Utility: convert image to grayscale
│
├── README.md                   # This file
├── GUIDE_UTILISATEUR.md        # Installation & usage guide (French)
├── TECHNICAL.md                # Technical pipeline documentation
│
└── ml-depth-pro/               # Apple ML Depth Pro (AI model)
    ├── src/depth_pro/          # The neural network model (Apple, unmodified)
    ├── License                 # Apple's license
    ├── ACKNOWLEDGEMENTS.md     # Third-party licenses (timm, DINOv2)
    ├── environment.yml         # Conda environment definition
    ├── pyproject.toml          # Python package configuration
    └── get_pretrained_models.sh
```

---

## Licenses

This repository contains code under multiple licenses:

| Code | Author | License |
|---|---|---|
| `launcher.py`, `generate_masks.py`, `generate_isolated_map.py`, `format_utils.py`, `dilate_image.py`, `cleanup.py`, `utils.py` | Eléonore Carlier | — |
| `run.py` | Apple Inc. / modified by Eléonore Carlier | Apple Sample Code License |
| `ml-depth-pro/src/` | Apple Inc. | Apple Sample Code License |
| timm, DINOv2 | Ross Wightman / Facebook Research | Apache 2.0 |

See [ml-depth-pro/License](ml-depth-pro/License) and [ml-depth-pro/ACKNOWLEDGEMENTS.md](ml-depth-pro/ACKNOWLEDGEMENTS.md) for full license texts.
