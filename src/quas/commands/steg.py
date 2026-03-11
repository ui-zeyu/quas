import heapq
import operator
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

from quas.core import UseCase
from quas.steg.basex import TABLE_BASE32, TABLE_BASE64, BaseXPayload, basex_decode
from quas.steg.zerowidth import ZeroWidthCrackItem

app = typer.Typer(name="steg", help="Steganography tools", no_args_is_help=True)


@app.callback()
def callback() -> None: ...


@dataclass(kw_only=True)
class Base32UseCase(UseCase[BaseXPayload]):
    """Extract hidden data from Base32 encoded strings."""

    GROUP = app
    COMMAND = "b32"

    infile: Annotated[Path, typer.Argument(help="Input file")]

    def execute(self) -> BaseXPayload:
        return basex_decode(self.infile.read_text().splitlines(), TABLE_BASE32)


@dataclass(kw_only=True)
class Base64UseCase(UseCase[BaseXPayload]):
    """Extract hidden data from Base64 encoded strings."""

    GROUP = app
    COMMAND = "b64"

    infile: Annotated[Path, typer.Argument(help="Input file")]

    def execute(self) -> BaseXPayload:
        return basex_decode(self.infile.read_text().splitlines(), TABLE_BASE64)


@dataclass(kw_only=True)
class ZeroWidthUseCase(UseCase[Iterable[ZeroWidthCrackItem]]):
    """Decode zero-width character steganography."""

    GROUP = app
    COMMAND = "zerowidth"

    text: Annotated[str | None, typer.Argument(help="Text to decode")] = None
    top: Annotated[
        int,
        typer.Option(
            "--top",
            "-t",
            help="Number of top results to display",
        ),
    ] = 10

    def execute(self) -> Iterable[ZeroWidthCrackItem]:
        from quas.steg.zerowidth import ZeroWidthDecoder

        text = self.text or sys.stdin.read()
        results = ZeroWidthDecoder.crack(text)
        return heapq.nlargest(self.top, results, operator.itemgetter(2))

    def effect(self, result: Iterable[ZeroWidthCrackItem]) -> None:
        table = Table("Charset", "Decoded Content", "Score", box=None)
        for steg, charset, score in result:
            charset_str = " ".join([repr(c).replace("'", "") for c in charset])
            table.add_row(charset_str, steg, f"{score:.2f}")
        self.ctx.obj["console"].print(table)
