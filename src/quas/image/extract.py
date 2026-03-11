from pathlib import Path

import numpy as np
from PIL import Image


def extract_pixels(
    infile: Path,
    x: int,
    y: int,
    stepx: int,
    stepy: int,
) -> Image.Image:
    img = Image.open(infile).convert("RGBA")
    arr = np.array(img)
    pixels = arr[y::stepy, x::stepx]
    out_img = Image.fromarray(pixels, "RGBA")
    return out_img
