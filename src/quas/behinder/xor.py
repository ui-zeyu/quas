from itertools import cycle
from pathlib import Path

import click

from quas.behinder.common import (
    _derive_behinder_key,
    _get_ciphertext,
    _get_passwords,
    _show_result,
)
from quas.context import ContextObject


@click.command(help="Decrypt Behinder XOR payload with wordlist")
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
