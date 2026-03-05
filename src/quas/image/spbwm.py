from enum import Enum, auto
from pathlib import Path
from typing import Protocol, override, runtime_checkable

import numpy as np
from PIL import Image
from scipy.fft import dctn

from quas.image.base import ImageResult

type ImageArray = np.ndarray[tuple[int, ...], np.dtype[np.uint8]]


class Mode(Enum):
    DFT_RESIZE = auto()
    DFT_PAD = auto()
    DFT_CROP = auto()
    DCT = auto()

    def to_extractor(
        self,
        image: Image.Image,
        brightness: float,
    ) -> SinglePictureBlindWatermarkExtractor:
        match self:
            case Mode.DFT_RESIZE:
                extractor = DFTResizeExtractor
            case Mode.DFT_PAD:
                extractor = DFTPadExtractor
            case Mode.DFT_CROP:
                extractor = DFTCropExtractor
            case Mode.DCT:
                extractor = DCTExtractor
        return extractor(image, brightness)

    @classmethod
    def perform(cls, infile: Path, mode: Mode, brightness: float) -> ImageResult:
        image = Image.open(infile)
        extractor = mode.to_extractor(image, brightness)
        watermark = extractor.extract()
        return ImageResult(watermark)


@runtime_checkable
class SinglePictureBlindWatermarkExtractor(Protocol):
    def __init__(self, image: Image.Image, brightness: float) -> None:
        self.image = image
        self.w, self.h = image.size
        self.scale_factor = brightness / 5

    def preprocess(self) -> ImageArray: ...

    def postprocess(self, array: ImageArray) -> Image.Image: ...

    def extract(self) -> Image.Image: ...


class DFTExtractor(SinglePictureBlindWatermarkExtractor):
    @override
    def __init__(self, image: Image.Image, brightness: float) -> None:
        super().__init__(image, brightness)
        self.nw, self.nh = self.calculate_size(self.w), self.calculate_size(self.h)

    def calculate_size(self, size: int) -> int:
        raise NotImplementedError

    @override
    def extract(self) -> Image.Image:
        array = self.preprocess()
        fft = np.fft.fft2(array, axes=(0, 1))
        modulus = np.abs(fft)

        sqrt_pixels = np.sqrt(self.nw * self.nh)
        watermark = np.around(modulus / sqrt_pixels) * self.scale_factor
        watermark = np.clip(watermark, 0, 255).astype(np.uint8)
        return self.postprocess(watermark)


class DFTResizeExtractor(DFTExtractor):
    @override
    def calculate_size(self, size: int) -> int:
        k = (size - 1).bit_length()
        lower, upper = 1 << (k - 1), 1 << k
        return lower if size - lower < upper - size else upper

    @override
    def preprocess(self) -> ImageArray:
        image = self.image.resize((self.nw, self.nh), Image.Resampling.LANCZOS)
        return np.array(image, dtype=np.float32)

    @override
    def postprocess(self, array: ImageArray) -> Image.Image:
        image = Image.fromarray(array)
        return image.resize((self.w, self.h), Image.Resampling.LANCZOS)


class DFTPadExtractor(DFTExtractor):
    @override
    def calculate_size(self, size: int) -> int:
        return 1 << (size - 1).bit_length()

    @override
    def preprocess(self) -> ImageArray:
        image = Image.new("RGB", (self.nw, self.nh), (0, 0, 0))
        image.paste(self.image, (0, 0))
        return np.array(image, dtype=np.float32)

    @override
    def postprocess(self, array: ImageArray) -> Image.Image:
        return Image.fromarray(array)


class DFTCropExtractor(DFTExtractor):
    @override
    def calculate_size(self, size: int) -> int:
        return 1 << (size.bit_length() - 1)

    @override
    def preprocess(self) -> ImageArray:
        image = self.image.crop((0, 0, self.nw, self.nh))
        return np.array(image, dtype=np.float32)

    @override
    def postprocess(self, array: ImageArray) -> Image.Image:
        return Image.fromarray(array)


class DCTExtractor(SinglePictureBlindWatermarkExtractor):
    @override
    def __init__(self, image: Image.Image, brightness: float):
        super().__init__(image, brightness)

    @override
    def preprocess(self) -> ImageArray:
        pad_h, pad_w = 0 if self.h & 1 == 0 else 1, 0 if self.w & 1 == 0 else 1
        array = np.array(self.image)
        if pad_h or pad_w:
            array = np.pad(array, ((0, pad_h), (0, pad_w), (0, 0)), mode="edge")
        return array

    @override
    def postprocess(self, array: ImageArray) -> Image.Image:
        return Image.fromarray(array)

    @override
    def extract(self) -> Image.Image:
        array = self.preprocess()
        dct_coeffs = dctn(array, axes=(0, 1), norm="ortho")
        watermark_mask = np.all((dct_coeffs >= 0) & (dct_coeffs <= 16), axis=-1)
        watermark = (watermark_mask * 255).astype(np.uint8)
        return self.postprocess(watermark)
