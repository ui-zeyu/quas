import sys
from base64 import b64decode
from dataclasses import dataclass
from typing import Annotated

import typer

from quas.core import UseCase
from quas.crypto.affine import AffinePayload, perform_affine_crack
from quas.crypto.analyse import AnalysePayload, perform_analysis
from quas.crypto.caesar import CaesarPayload, perform_caesar_crack
from quas.crypto.columnar import ColumnarPayload, perform_columnar_crack
from quas.crypto.railfence import RailFencePayload, perform_railfence_crack
from quas.crypto.substitute import SubPayload, perform_sub_crack
from quas.crypto.xor import XorPayload, perform_xor_crack

app = typer.Typer(
    name="crypto", help="Classical cryptography tools", no_args_is_help=True
)


@app.callback()
def callback() -> None: ...


def get_ciphertext(ciphertext: str | None) -> str:
    return (ciphertext or sys.stdin.read()).strip()


@dataclass(kw_only=True)
class CryptoUseCase[O](UseCase[O]):
    ciphertext: Annotated[
        str | None,
        typer.Argument(help="Ciphertext (optional, reads from stdin if omitted)"),
    ] = None
    top: Annotated[
        int,
        typer.Option(
            "--top",
            "-t",
            help="Show top N results",
        ),
    ] = 10

    def effect(self, result: O) -> None:
        self.ctx.obj["console"].print(result, markup=False)


@dataclass(kw_only=True)
class AffineUseCase(CryptoUseCase[AffinePayload]):
    """Bruteforce affine cipher with N-gram scoring."""

    GROUP = app
    COMMAND = "affine"

    def execute(self) -> AffinePayload:
        ciphertext = get_ciphertext(self.ciphertext)
        return perform_affine_crack(ciphertext, self.top)


@dataclass(kw_only=True)
class AnalyseUseCase(UseCase[AnalysePayload]):
    """Analyze ciphertext statistics using various scoring methods."""

    GROUP = app
    COMMAND = "analyse"

    ciphertext: Annotated[
        str | None,
        typer.Argument(help="Ciphertext (optional, reads from stdin if omitted)"),
    ] = None
    hex_flag: Annotated[
        bool,
        typer.Option(
            "--hex",
            help="Input is hex-encoded, decode first",
        ),
    ] = False
    b64_flag: Annotated[
        bool,
        typer.Option(
            "--base64",
            help="Input is base64-encoded, decode first",
        ),
    ] = False

    def execute(self) -> AnalysePayload:
        if self.hex_flag and self.b64_flag:
            raise typer.BadParameter("Cannot specify both --hex and --base64")

        ciphertext = get_ciphertext(self.ciphertext)
        if self.hex_flag:
            ciphertext = bytes.fromhex(ciphertext).decode(errors="ignore")
        elif self.b64_flag:
            ciphertext = b64decode(ciphertext).decode(errors="ignore")
        ciphertext = ciphertext.strip()

        return perform_analysis(ciphertext)

    def effect(self, result: AnalysePayload) -> None:
        self.ctx.obj["console"].print(result)


@dataclass(kw_only=True)
class CaesarUseCase(CryptoUseCase[CaesarPayload]):
    """Bruteforce caesar cipher with quadgram scoring."""

    GROUP = app
    COMMAND = "caesar"

    def execute(self) -> CaesarPayload:
        ciphertext = get_ciphertext(self.ciphertext)
        return perform_caesar_crack(ciphertext, self.top)


@dataclass(kw_only=True)
class ColumnarUseCase(CryptoUseCase[ColumnarPayload]):
    """Crack columnar transposition cipher with quadgram scoring."""

    GROUP = app
    COMMAND = "columnar"

    def execute(self) -> ColumnarPayload:
        ciphertext = get_ciphertext(self.ciphertext)
        return perform_columnar_crack(ciphertext, self.top)


@dataclass(kw_only=True)
class RailfenceUseCase(CryptoUseCase[RailFencePayload]):
    """Crack rail fence cipher with quadgram scoring."""

    GROUP = app
    COMMAND = "railfence"

    def execute(self) -> RailFencePayload:
        ciphertext = get_ciphertext(self.ciphertext)
        return perform_railfence_crack(ciphertext, self.top)


@dataclass(kw_only=True)
class SubUseCase(CryptoUseCase[SubPayload]):
    """Crack substitution cipher using hill climbing with N-gram scoring."""

    GROUP = app
    COMMAND = "sub"

    calphabet: Annotated[
        str,
        typer.Option(
            "--alphabet",
            "-a",
            help="Alphabet used in ciphertext (space-separated or string)",
        ),
    ] = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
    restarts: Annotated[
        int,
        typer.Option(
            "--restarts",
            "-r",
            help="Number of hill climbing restarts",
        ),
    ] = 10

    def execute(self) -> SubPayload:
        ciphertext = get_ciphertext(self.ciphertext)
        return perform_sub_crack(
            ciphertext,
            self.calphabet,
            self.restarts,
            self.top,
        )


@dataclass(kw_only=True)
class XorUseCase(CryptoUseCase[XorPayload]):
    """Crack XOR cipher using frequency analysis."""

    GROUP = app
    COMMAND = "xor"

    def execute(self) -> XorPayload:
        ciphertext = get_ciphertext(self.ciphertext)
        return perform_xor_crack(ciphertext, self.top)
