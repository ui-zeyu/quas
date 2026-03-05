from pathlib import Path

import numpy as np
from PIL import Image

from quas.image.base import ImageResult


def extract_pixels(
    infile: Path,
    x: int,
    y: int,
    stepx: int,
    stepy: int,
) -> ImageResult:
    img = Image.open(infile).convert("RGBA")
    arr = np.array(img)
    pixels = arr[y::stepy, x::stepx]
    out_img = Image.fromarray(pixels, "RGBA")
    return ImageResult(out_img)
