import random
from pathlib import Path

import click
import numpy as np
import random2
from PIL import Image

type ImageArray = np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]


class DoublePictureBlindWatermarkExtractor:
    @classmethod
    def _load_as_bgr(cls, path: Path) -> ImageArray:
        with Image.open(path).convert("RGB") as img:
            arr = np.array(img, dtype=np.uint8)
        return arr[..., ::-1]

    def __init__(self, original: Path, watermarked: Path, seed: int, old: bool) -> None:
        self.original = self._load_as_bgr(original)
        self.watermarked = self._load_as_bgr(watermarked)
        self.random = random2 if old else random
        self.random.seed(seed)

    def _generate_shuffle_indices(self, size: int) -> list[int]:
        indices = list(range(size))
        self.random.shuffle(indices)
        return indices

    def _reverse_shuffle(self, watermark: ImageArray) -> ImageArray:
        h, w, _ = watermark.shape

        h_half = h // 2
        row_idx = self._generate_shuffle_indices(h_half)
        col_idx = self._generate_shuffle_indices(w)

        restored = np.zeros_like(watermark)
        restored[np.ix_(row_idx, col_idx)] = watermark[:h_half, :]
        restored[h_half:, :] = restored[:h_half, :][::-1, ::-1]
        return restored

    def extract(self) -> Image.Image:
        watermark = np.real(np.fft.fft2(self.original) - np.fft.fft2(self.watermarked))
        watermark = np.clip(watermark, 0, 255).astype(np.uint8)
        watermark = self._reverse_shuffle(watermark)
        return Image.fromarray(watermark)


@click.command()
@click.option(
    "-s",
    "--seed",
    default=20160930,
    help="Default seed for BlindWaterMark, try height + width for blind-watermark",
)
@click.option("--old", is_flag=True, help="Use Python2 random algorithm")
@click.argument("original", type=Path)
@click.argument("watermarked", type=Path)
@click.argument("outfile", type=Path, required=False)
def dpbwm(
    seed: int,
    old: bool,
    original: Path,
    watermarked: Path,
    outfile: Path | None,
) -> None:
    extractor = DoublePictureBlindWatermarkExtractor(original, watermarked, seed, old)
    watermark = extractor.extract()
    watermark.show() if outfile is None else watermark.save(outfile)
