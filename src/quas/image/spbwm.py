from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import override

import click
import numpy as np
from PIL import Image

from quas.context import ContextObject


class ResizeMode(Enum):
    RESIZE = auto()
    PAD = auto()
    CROP = auto()

    def to_extractor(
        self,
        image: Image.Image,
        brightness: float,
    ) -> SinglePictureBlindWatermarkExtractor:
        match self:
            case ResizeMode.RESIZE:
                extractor = ResizeExtractor
            case ResizeMode.PAD:
                extractor = PadExtractor
            case ResizeMode.CROP:
                extractor = CropExtractor
        return extractor(image, brightness)


class SinglePictureBlindWatermarkExtractor(ABC):
    def __init__(self, image: Image.Image, brightness: float) -> None:
        self.image = image
        self.w, self.h = image.size
        self.nw, self.nh = self.calculate_size(self.w), self.calculate_size(self.h)
        self.scale_factor = brightness / 5

    @abstractmethod
    def calculate_size(self, size: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def preprocess(self) -> Image.Image:
        raise NotImplementedError

    @abstractmethod
    def postprocess(self, image: Image.Image) -> Image.Image:
        raise NotImplementedError

    def extract(self) -> Image.Image:
        image = self.preprocess()
        array = np.array(image, dtype=np.float32)

        fft = np.fft.fft2(array, axes=(0, 1))
        modulus = np.abs(fft)

        sqrt_pixels = np.sqrt(self.nw * self.nh)
        watermark = np.around(modulus / sqrt_pixels) * self.scale_factor
        watermark = np.clip(watermark, 0, 255).astype(np.uint8)

        image = Image.fromarray(watermark, mode="RGB")
        return self.postprocess(image)


class ResizeExtractor(SinglePictureBlindWatermarkExtractor):
    @override
    def calculate_size(self, size: int) -> int:
        k = (size - 1).bit_length()
        lower, upper = 1 << (k - 1), 1 << k
        return lower if size - lower < upper - size else upper

    @override
    def preprocess(self) -> Image.Image:
        return self.image.resize((self.nw, self.nh), Image.Resampling.LANCZOS)

    @override
    def postprocess(self, image: Image.Image) -> Image.Image:
        return image.resize((self.w, self.h), Image.Resampling.LANCZOS)


class PadExtractor(SinglePictureBlindWatermarkExtractor):
    @override
    def calculate_size(self, size: int) -> int:
        return 1 << (size - 1).bit_length()

    @override
    def preprocess(self) -> Image.Image:
        image = Image.new("RGB", (self.nw, self.nh), (0, 0, 0))
        image.paste(self.image, (0, 0))
        return image

    @override
    def postprocess(self, image: Image.Image) -> Image.Image:
        return image


class CropExtractor(SinglePictureBlindWatermarkExtractor):
    @override
    def calculate_size(self, size: int) -> int:
        return 1 << (size.bit_length() - 1)

    @override
    def preprocess(self) -> Image.Image:
        return self.image.crop((0, 0, self.nw, self.nh))

    @override
    def postprocess(self, image: Image.Image) -> Image.Image:
        return image


@click.command(
    help="Extract single image blind watermark using FFT frequency domain analysis",
)
@click.pass_obj
@click.argument("infile", type=Path)
@click.argument("outfile", type=Path, required=False)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(ResizeMode, case_sensitive=False),
    default=ResizeMode.RESIZE,
    help="Processing mode: resize (stretch), pad (black border), or crop (trim)",
)
@click.option("-b", "--brightness", type=float, default=50)
def spbwm(
    ctx: ContextObject,
    infile: Path,
    outfile: Path | None,
    mode: ResizeMode,
    brightness: float,
) -> None:
    console = ctx["console"]

    image = Image.open(infile)
    extractor = mode.to_extractor(image, brightness)
    watermark = extractor.extract()

    if outfile:
        watermark.save(outfile)
        console.print(f"[green]Watermark saved to:[/green] {outfile}")
    else:
        watermark.show()
