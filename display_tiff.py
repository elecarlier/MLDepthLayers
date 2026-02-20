"""Display all pages of a TIFF file using matplotlib.

Usage:
    python display_tiff.py                         # looks in output/final/
    python display_tiff.py path/to/folder_or_file  # custom path
"""

import sys
import matplotlib.pyplot as plt
import tifffile as tiff
from pathlib import Path


def display_tiff(tiff_path: Path):
    with tiff.TiffFile(tiff_path) as tif:
        print(f"Displaying: {tiff_path}")
        print(f"Pages: {len(tif.pages)}  |  Series: {len(tif.series)}")
        for i, page in enumerate(tif.pages):
            img = page.asarray()
            if img.dtype.kind == "f" and img.max() > 1.0:
                img = img.astype("uint8")
            plt.figure(figsize=(5, 5))
            if img.ndim == 2:
                plt.imshow(img, cmap="gray")
            else:
                plt.imshow(img)
            plt.title(f"Page {i}")
            plt.axis("off")
            plt.show()


def main():
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = Path("output/final")

    if target.is_file():
        display_tiff(target)
    elif target.is_dir():
        tiff_files = sorted(target.glob("*.tiff")) + sorted(target.glob("*.tif"))
        if not tiff_files:
            raise RuntimeError(f"No TIFF files found in {target}")
        for f in tiff_files:
            display_tiff(f)
    else:
        raise FileNotFoundError(f"Path not found: {target}")


if __name__ == "__main__":
    main()
