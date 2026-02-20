# Technical Documentation — MLDepthLayers

**Author: Eléonore Carlier**

This document describes the pipeline architecture, each script's role, folder conventions, and available options.

---

## Overview

MLDepthLayers is a pipeline that generates isolated per-layer depth maps from a layered PSD file. It wraps Apple's [ML Depth Pro](https://github.com/apple/ml-depth-pro) model and adds a full automation layer on top: PSD extraction, mask generation, depth isolation, and structured export.

---

## Pipeline

```
PSD file
  └─> 1. extract_layers()       →  input/layers/*.png
  └─> 2. generate_masks()       →  output/masks/*_mask.png
  └─> 3. generate_depth_maps()  →  output/depth_maps_layers/*_map.jpg
        (runs Depth Pro on each isolated layer PNG individually)
  └─> 4. isolate_layers()       →  output/isolated_layers/*_isolated.png
        (masks applied to per-layer depth maps → layers_map/)
  └─> 5. isolate_from_masks()   →  output/isolated_global/*_isolated.png
        (masks applied to the global depth map → global_map/)
  └─> 6. export_results()       →  <psd_dir>/global_map/ & <psd_dir>/layers_map/
```

An optional side-by-side step (original + depth map) runs between steps 4 and 5 if `-s` is passed.

**The two output folders produce different results by design:**
- **`layers_map/`** — depth computed from each layer individually. The model only sees the isolated element, so depth is relative to the object itself.
- **`global_map/`** — depth computed from the full composite image, then each layer's mask is applied to extract the corresponding region. Depth reflects each element's position within the whole scene.

---

## Entry point

### `launcher.py`

The main script. Orchestrates the full pipeline.

```bash
python launcher.py [options] path/to/file.psd
```

**Arguments:**

| Argument | Type | Description |
|---|---|---|
| `psd_path` | positional | Path to the input `.psd` file |
| `-v`, `--verbose` | flag | Enable detailed logging |
| `-s`, `--side` | flag | Generate side-by-side image for the global layer |
| `-c`, `--cleanup` | flag | Run `cleanup.py` before the pipeline starts |

**Working directories created at runtime:**

| Path | Content |
|---|---|
| `input/layers/` | PNG layers extracted from the PSD |
| `output/masks/` | Binary masks (one per layer) |
| `output/depth_maps_layers/` | Raw depth maps from ML Depth Pro |
| `output/isolated_layers/` | Depth maps masked per layer |
| `output/isolated_global/` | Depth maps from the global image, masked per layer |

---

## Scripts

### `run.py`

Modified from Apple's original `src/cli/run.py`. Runs ML Depth Pro inference on a single image and saves the result as a grayscale JPEG depth map (`*_map.jpg`).

Key modifications from the original:
- `--skip-display` defaults to `True` (no matplotlib window)
- Saves depth map in **grayscale** (not colormap) using `gray` cmap
- Adds `-s`/`--side` option to generate a side-by-side image (`*_lkg.jpg`)
- Handles RGBA input images (strips alpha before concatenation)

Called internally by `launcher.py` via `subprocess`.

---

### `generate_masks.py`

Reads each PNG from `input/layers/`, extracts its alpha channel, and saves a binary mask to `output/masks/`.

- Pixels with alpha > 5% → white (255)
- Pixels with alpha ≤ 5% → black (0)
- Output: `output/masks/<layer_name>_mask.png`

---

### `generate_isolated_map.py`

Contains two functions:

**`isolate_single_depth(depth_path, mask_path, output_path)`**
Applies a single mask to a depth map. Outside the mask → fully transparent (RGBA with alpha=0).

**`isolate_all_depths(depth_dir, masks_dir, output_dir)`**
Batch version. Matches files by naming convention:
- `0000_LayerName_map.jpg` → `0000_LayerName_mask.png`
- Output: `0000_LayerName_isolated.png`

**`isolate_from_masks(images_dir, fallback_dir, masks_dir, output_dir)`**
Applies all masks to the global depth map. Used for `output/isolated_global/`.

---

### `format_utils.py`

**`psd_to_png(input_psd, output_folder)`**
Extracts all visible layers from a PSD into PNG files at full PSD canvas size, preserving each layer's exact position. Groups are traversed recursively. Layers whose name ends with ` map` are skipped (to avoid re-processing existing depth maps). Output filenames: `0000_LayerName.png`, `0001_LayerName.png`, etc. The last file is treated as the global (composite) image.

**`clean_name(filename)`**
Normalises isolated file names for the final export:
`0000_LayerName_mask_isolated.png` → `LayerName map.png`

**`export_final_folders(psd_path, isolated_global_dir, isolated_layers_dir)`**
Copies and renames files from the working `output/` directories into two clean folders next to the original PSD:
- `<psd_dir>/global_map/`
- `<psd_dir>/layers_map/`

---

### `dilate_image.py`

**`dilate_images(input_dir, output_dir, scale=1.15)`**
Scales each depth map image by `scale` (default 15%) and crops back to the original canvas size, centred. This slightly expands the depth content to avoid hard edges at layer boundaries. Used optionally — not called in the default pipeline.

---

### `cleanup.py`

**`clean_input_output(folders, exts)`**
Deletes all image files (`.png`, `.jpg`, `.jpeg` by default) from `input/` and `output/` recursively. Called by `launcher.py -c` or directly:

```bash
python cleanup.py
```

---

### `utils.py`

Shared utility functions (not all are used in the main pipeline):

- **`depth_to_uint8(depth)`** — Normalises a float depth array to 0–255 uint8
- **`expand_depth_inside(depth_map_path, mask, expand_px, interior_px)`** — Fills a halo around a masked object by sampling depth values from inside the object boundary (used for edge blending experiments)
- **`dilate_image(image_path, expand_px)`** — Dilates the alpha channel of an RGBA image
- **`tiff_to_pngs(tiff_path, output_folder)`** — Extracts all pages of a TIFF into individual PNGs

---

### `display_tiff.py`

Utility to display TIFF pages using matplotlib. Accepts an optional path argument:

```bash
python display_tiff.py                        # looks in output/final/
python display_tiff.py path/to/folder_or_file
```

---

## Naming conventions

Layer files follow a zero-padded index prefix: `0000_`, `0001_`, etc. This ensures consistent alphabetical ordering throughout the pipeline. The suffix `_mask`, `_map`, `_isolated` are appended/stripped at each stage.

| Stage | Filename pattern |
|---|---|
| Extracted layers | `0000_LayerName.png` |
| Masks | `0000_LayerName_mask.png` |
| Depth maps | `0000_LayerName_map.jpg` |
| Isolated depths | `0000_LayerName_isolated.png` |
| Final export | `LayerName map.png` |

---

## Dependencies

All dependencies are managed via the Conda environment defined in `ml-depth-pro/environment.yml`.

Key packages:

| Package | Role |
|---|---|
| `depth_pro` | Apple's ML Depth Pro model (installed via `pip install -e .`) |
| `psd-tools` | PSD file parsing and layer extraction |
| `opencv` | Image processing (masking, thresholding) |
| `Pillow` | Image I/O |
| `numpy` | Array operations |
| `scipy` | Binary dilation / morphological operations |
| `tifffile` | TIFF reading/writing |
| `torch` / `torchvision` | Neural network inference |
| `timm` | Vision transformer backbone (used by Depth Pro) |

---

## Licenses

- `launcher.py`, `generate_masks.py`, `generate_isolated_map.py`, `format_utils.py`, `dilate_image.py`, `cleanup.py`, `utils.py`: written by Eléonore Carlier
- `run.py`: modified from Apple's original — Copyright © 2024 Apple Inc., modifications by Eléonore Carlier
- `ml-depth-pro/src/depth_pro/`: Apple ML Depth Pro — Copyright © 2024 Apple Inc. — see [`ml-depth-pro/License`](ml-depth-pro/License)
- `timm`, `DINOv2`: Apache License 2.0 — see [`ml-depth-pro/ACKNOWLEDGEMENTS.md`](ml-depth-pro/ACKNOWLEDGEMENTS.md)
