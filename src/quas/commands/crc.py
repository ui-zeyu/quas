import os
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import toolz
import typer

from quas.core import UseCase
from quas.crc.ihdr import IHDRPayload
from quas.crc.ihdr import crack as ihdr_crack
from quas.crc.zip import ZipPayload
from quas.crc.zip import crack as zip_crack

app = typer.Typer(name="crc", help="CRC32 bruteforce tools", no_args_is_help=True)


@app.callback()
def callback() -> None: ...


@dataclass(kw_only=True)
class IHDRUseCase(UseCase[IHDRPayload]):
    """Recover PNG IHDR dimensions by bruteforcing CRC32."""

    GROUP = app
    COMMAND = "ihdr"

    infile: Annotated[Path, typer.Argument(help="Input PNG file")]
    outfile: Annotated[
        Path | None, typer.Argument(help="Output PNG file (optional)")
    ] = None
    max_width: Annotated[
        int,
        typer.Option("--max-width", help="Maximum width to search"),
    ] = 5000
    max_height: Annotated[
        int,
        typer.Option("--max-height", help="Maximum height to search"),
    ] = 5000

    def execute(self) -> IHDRPayload:
        data = self.infile.read_bytes()
        if results := ihdr_crack(data, self.max_width, self.max_height):
            return results
        raise ValueError("Failed to find matching dimensions")

    def effect(self, result: IHDRPayload) -> None:
        console = self.ctx.obj["console"]
        console.print(result)

        if self.outfile:
            result.image.save(self.outfile)
        else:
            result.image.show()


@dataclass(kw_only=True)
class ZipUseCase(UseCase[ZipPayload]):
    """Bruteforce ZIP filenames by CRC32."""

    GROUP = app
    COMMAND = "zip"

    infile: Annotated[Path, typer.Argument(help="Input ZIP file")]
    size: Annotated[int, typer.Option("--size", "-s", help="Target file size to match")]
    charset: Annotated[
        str,
        typer.Option(
            "--charset",
            "-c",
            help="Character set for bruteforce",
        ),
    ] = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "
    jobs: Annotated[
        int | None,
        typer.Option(
            "--jobs",
            "-j",
            help="Number of jobs to run",
        ),
    ] = None

    def execute(self) -> ZipPayload:
        jobs = self.jobs or os.cpu_count() or 1
        charset = self.charset
        size = self.size
        infile = self.infile

        charset_bytes: bytes = f" {charset} ".encode()
        alphabet = bytearray()
        for p, x, n in toolz.sliding_window(3, charset_bytes):
            if x == ord("-") and p < n:
                alphabet.extend(range(p + 1, n))
            else:
                alphabet.append(x)

        with zipfile.ZipFile(infile, "r") as zf:
            crc2file = {f.CRC: f.filename for f in zf.infolist() if f.file_size == size}
            return zip_crack(
                size, set(crc2file.keys()), bytes(alphabet), jobs, crc2file
            )

    def effect(self, result: ZipPayload) -> None:
        self.ctx.obj["console"].print(result)
