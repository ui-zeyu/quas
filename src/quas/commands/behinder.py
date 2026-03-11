import sys
from base64 import b64decode
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from quas.behinder.aes import Mode
from quas.core import UseCase

if TYPE_CHECKING:
    from quas.behinder import BehinderPayload

app = typer.Typer(
    name="behinder", help="Behinder payload decryption tools", no_args_is_help=True
)


@app.callback()
def callback() -> None: ...


def get_ciphertext(ciphertext: str | None) -> bytes:
    ciphertext = sys.stdin.read() if ciphertext is None else ciphertext
    return b64decode(ciphertext.strip())


def get_passwords(password_path: Path) -> Sequence[bytes]:
    return (
        password_path.read_bytes().splitlines()
        if password_path.exists()
        else [str(password_path).encode()]
    )


@dataclass(kw_only=True)
class BehinderUseCase(UseCase["BehinderPayload"]):
    ciphertext: Annotated[
        str | None,
        typer.Argument(
            help="Base64 encoded ciphertext (optional, reads from stdin if omitted)"
        ),
    ] = None
    wordlist: Annotated[
        Path,
        typer.Option(
            "--wordlist",
            "-w",
            help="Wordlist file path or single password",
        ),
    ]

    def effect(self, result: BehinderPayload) -> None:
        self.ctx.obj["console"].print(result)


@dataclass(kw_only=True)
class AesUseCase(BehinderUseCase):
    """Decrypt Behinder AES payload with wordlist."""

    GROUP = app
    COMMAND = "aes"

    mode: Annotated[
        Mode,
        typer.Option(
            "--mode",
            "-m",
            help="AES mode (ECB or CBC)",
        ),
    ] = Mode.ECB

    def execute(self) -> BehinderPayload:
        from quas.behinder.aes import decrypt as aes_decrypt

        ciphertext = get_ciphertext(self.ciphertext)
        passwords = get_passwords(self.wordlist)
        if result := aes_decrypt(ciphertext, passwords, self.mode):
            return result
        raise ValueError("No valid password found")


@dataclass(kw_only=True)
class XorUseCase(BehinderUseCase):
    """Decrypt Behinder XOR payload with wordlist."""

    GROUP = app
    COMMAND = "xor"

    def execute(self) -> BehinderPayload:
        from quas.behinder.xor import decrypt as xor_decrypt

        ciphertext = get_ciphertext(self.ciphertext)
        passwords = get_passwords(self.wordlist)
        if result := xor_decrypt(ciphertext, passwords):
            return result
        raise ValueError("No valid password found")
