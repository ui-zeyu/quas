import sys
from base64 import b64decode
from collections.abc import Sequence
from pathlib import Path

import click

from quas.behinder.aes import Mode, decrypt
from quas.behinder.base import BehinderResult
from quas.commands.context import ContextObject


def get_ciphertext(ciphertext: str | None) -> bytes:
    ciphertext = sys.stdin.read() if ciphertext is None else ciphertext
    return b64decode(ciphertext.strip())


def get_passwords(password: Path) -> Sequence[bytes]:
    return (
        password.read_bytes().splitlines()
        if password.exists()
        else [str(password).encode()]
    )


@click.group(help="Behinder webshell tools")
def app() -> None: ...


@click.command(help="Decrypt Behinder AES payload with wordlist")
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
    ct = get_ciphertext(ciphertext)
    passwords = get_passwords(wordlist)

    if payload := decrypt(ct, passwords, mode):
        console.print(BehinderResult(payload))


@click.command(help="Decrypt Behinder XOR payload with wordlist")
@click.pass_obj
@click.argument("ciphertext", required=False)
@click.option("-w", "--wordlist", type=Path, required=True, help="Wordlist file path")
def xor(ctx: ContextObject, ciphertext: str | None, wordlist: Path) -> None:
    from quas.behinder.base import BehinderResult
    from quas.behinder.xor import decrypt

    console = ctx["console"]
    ct = get_ciphertext(ciphertext)
    passwords = get_passwords(wordlist)

    if payload := decrypt(ct, passwords):
        console.print(BehinderResult(payload))


app.add_command(aes)
app.add_command(xor)
