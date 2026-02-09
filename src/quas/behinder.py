import enum
import sys
from base64 import b64decode
from collections.abc import Sequence
from hashlib import md5
from itertools import cycle
from pathlib import Path

import click
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad

from quas.context import ContextObject

IV = b"\x00" * AES.block_size
MAX_PLAINTEXT_DISPLAY = 60


class Mode(enum.Enum):
    ECB = AES.MODE_ECB
    CBC = AES.MODE_CBC


def _get_ciphertext(ciphertext: str | None) -> bytes:
    ciphertext = sys.stdin.read().strip() if ciphertext is None else ciphertext
    return b64decode(ciphertext)


def _get_passwords(password: Path) -> Sequence[bytes]:
    return (
        password.read_bytes().splitlines()
        if password.exists()
        else [str(password).encode()]
    )


def _truncate_plaintext(plaintext: str) -> str:
    return (
        plaintext[:MAX_PLAINTEXT_DISPLAY] + "..."
        if len(plaintext) > MAX_PLAINTEXT_DISPLAY
        else plaintext
    )


def _derive_behinder_key(password: bytes) -> bytes:
    return md5(password).digest()[:16]


def _show_result(console, password: bytes, key: bytes, plaintext: str) -> None:
    console.print(f"[bold cyan]Password:[/bold cyan] {password.decode()}")
    console.print(f"[bold magenta]Key:[/bold magenta] {key}")
    console.print(
        f"[bold green]Plaintext:[/bold green] {_truncate_plaintext(plaintext)}"
    )


@click.group()
def app() -> None: ...


@app.command(help="Decrypt Behinder AES payload with wordlist")
@click.pass_obj
@click.argument("ciphertext", required=False)
@click.option("-w", "--wordlist", type=Path, required=True, help="Wordlist file path")
@click.option(
    "-m",
    "--mode",
    type=click.Choice(Mode, case_sensitive=False),
    default=Mode.ECB,
    help="AES mode (ECB or CBC)",
)
def aes(ctx: ContextObject, ciphertext: str | None, wordlist: Path, mode: Mode) -> None:
    console = ctx["console"]
    ct = _get_ciphertext(ciphertext)
    passwords = _get_passwords(wordlist)

    for password in passwords:
        key = _derive_behinder_key(password)
        cipher = (
            AES.new(key, mode.value)
            if mode == Mode.ECB
            else AES.new(key, mode.value, iv=IV)
        )

        try:
            plaintext = unpad(cipher.decrypt(ct), AES.block_size).decode()
            _show_result(console, password, key, plaintext)
            break
        except UnicodeDecodeError, ValueError:
            continue


@app.command(help="Decrypt Behinder XOR payload with wordlist")
@click.pass_obj
@click.argument("ciphertext", required=False)
@click.option("-w", "--wordlist", type=Path, required=True, help="Wordlist file path")
def xor(ctx: ContextObject, ciphertext: str | None, wordlist: Path) -> None:
    console = ctx["console"]
    ct = _get_ciphertext(ciphertext)
    passwords = _get_passwords(wordlist)

    for password in passwords:
        key = _derive_behinder_key(password)
        key = key[1:] + key[:1]
        plaintext = bytes(x ^ y for x, y in zip(ct, cycle(key), strict=True))

        try:
            decoded = plaintext.decode()
            _show_result(console, password, key, decoded)
            break
        except UnicodeDecodeError:
            continue
