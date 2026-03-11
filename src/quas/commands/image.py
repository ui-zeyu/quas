import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from quas.core import UseCase
from quas.image.spbwm import Mode

if TYPE_CHECKING:
    from PIL import Image

    from quas.image.inspect import InspectPayload
    from quas.image.lsbaes import LsbAesPayload

app = typer.Typer(name="image", help="Image analysis tools", no_args_is_help=True)


@app.callback()
def callback() -> None: ...


@dataclass(kw_only=True)
class ImageUseCase[O](UseCase[O]):
    infile: Annotated[Path, typer.Argument(help="Input image file")]


@dataclass(kw_only=True)
class ExtractUseCase(ImageUseCase["Image.Image"]):
    """Extract image pixels by coordinate sampling."""

    GROUP = app
    COMMAND = "extract"

    outfile: Annotated[
        Path | None, typer.Argument(help="Output image file (optional)")
    ] = None
    x: Annotated[int, typer.Option("-x", help="Starting x coordinate")] = 0
    y: Annotated[int, typer.Option("-y", help="Starting y coordinate")] = 0
    stepx: Annotated[int, typer.Option("--stepx", help="X step size")] = 1
    stepy: Annotated[int, typer.Option("--stepy", help="Y step size")] = 1

    def execute(self) -> Image.Image:
        from quas.image.extract import extract_pixels

        return extract_pixels(
            self.infile,
            self.x,
            self.y,
            self.stepx,
            self.stepy,
        )

    def effect(self, result: Image.Image) -> None:
        if self.outfile:
            result.save(self.outfile)
        else:
            result.show()


@dataclass(kw_only=True)
class InspectUseCase(ImageUseCase["InspectPayload"]):
    """Inspect image pixels by coordinate sampling."""

    GROUP = app
    COMMAND = "inspect"

    x: Annotated[int, typer.Option("-x", help="Starting x coordinate")] = 0
    y: Annotated[int, typer.Option("-y", help="Starting y coordinate")] = 0
    stepx: Annotated[int, typer.Option("--stepx", help="X step size")] = 1
    stepy: Annotated[int, typer.Option("--stepy", help="Y step size")] = 1
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-c",
            help="Number of pixels to display (0 for all)",
        ),
    ] = 10

    def execute(self) -> InspectPayload:
        from quas.image.inspect import perform_inspect

        return perform_inspect(
            self.infile,
            self.x,
            self.y,
            self.stepx,
            self.stepy,
            self.count,
        )

    def effect(self, result: InspectPayload) -> None:
        self.ctx.obj["console"].print(result)


@dataclass(kw_only=True)
class LsbaesUseCase(UseCase["LsbAesPayload | None"]):
    """Extract AES-encrypted data hidden in LSB bits and brute-force password."""

    GROUP = app
    COMMAND = "lsbaes"

    image_path: Annotated[Path, typer.Argument(help="Input image file")]
    wordlist: Annotated[Path, typer.Argument(help="Wordlist file path")]
    workers: Annotated[
        int | None,
        typer.Option(
            "--workers",
            "-w",
            help="Number of worker processes",
        ),
    ] = None

    def execute(self) -> LsbAesPayload | None:
        from quas.image.lsbaes import perform_lsbaes

        console = self.ctx.obj["console"]
        workers = self.workers or os.cpu_count() or 12

        return perform_lsbaes(self.image_path, self.wordlist, workers, console)

    def effect(self, result: LsbAesPayload | None) -> None:
        if result:
            self.ctx.obj["console"].print(result)


@dataclass(kw_only=True)
class SpbwmUseCase(ImageUseCase["Image.Image"]):
    """Extract single image blind watermark using frequency domain analysis."""

    GROUP = app
    COMMAND = "spbwm"

    outfile: Annotated[
        Path | None, typer.Argument(help="Output image file (optional)")
    ] = None
    mode: Annotated[
        Mode,
        typer.Option(
            "--mode",
            "-m",
            help="Processing mode",
        ),
    ] = Mode.DFT_RESIZE
    brightness: Annotated[
        float,
        typer.Option(
            "--brightness",
            "-b",
            help="Watermark brightness enhancement factor",
        ),
    ] = 50.0

    def execute(self) -> Image.Image:
        return Mode.perform(self.infile, self.mode, self.brightness)

    def effect(self, result: Image.Image) -> None:
        if self.outfile:
            result.save(self.outfile)
        else:
            result.show()


@dataclass(kw_only=True)
class DpbwmUseCase(UseCase["Image.Image"]):
    """Extract double image blind watermark."""

    GROUP = app
    COMMAND = "dpbwm"

    original: Annotated[Path, typer.Argument(help="Original image file")]
    watermarked: Annotated[Path, typer.Argument(help="Watermarked image file")]
    outfile: Annotated[
        Path | None, typer.Argument(help="Output image file (optional)")
    ] = None
    seed: Annotated[
        int,
        typer.Option(
            "--seed",
            "-s",
            help="Default seed for BlindWaterMark",
        ),
    ] = 20160930
    old: Annotated[bool, typer.Option("--old", help="Use Python2 random algorithm")] = (
        False
    )

    def execute(self) -> Image.Image:
        from quas.image.dpbwm import DoublePictureBlindWatermarkExtractor

        return DoublePictureBlindWatermarkExtractor.perform(
            self.original,
            self.watermarked,
            self.seed,
            self.old,
        )

    def effect(self, result: Image.Image) -> None:
        if self.outfile:
            result.save(self.outfile)
        else:
            result.show()
