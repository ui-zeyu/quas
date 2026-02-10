import enum
from pathlib import Path

import click
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad

from quas.behinder.common import (
    IV,
    _derive_behinder_key,
    _get_ciphertext,
    _get_passwords,
    _show_result,
)
from quas.context import ContextObject


class Mode(enum.Enum):
    ECB = AES.MODE_ECB
    CBC = AES.MODE_CBC


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
