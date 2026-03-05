from pathlib import Path

import click

from quas.context import ContextObject


@click.group(help="Behinder webshell tools")
def app() -> None: ...


@click.command(help="Decrypt Behinder AES payload with wordlist")
@click.pass_obj
@click.argument("ciphertext", required=False)
@click.option("-w", "--wordlist", type=Path, required=True, help="Wordlist file path")
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["ECB", "CBC"], case_sensitive=False),
    default="ECB",
    help="AES mode (ECB or CBC)",
)
def aes(ctx: ContextObject, ciphertext: str | None, wordlist: Path, mode: str) -> None:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import unpad

    from quas.behinder.common import (
        IV,
        _derive_behinder_key,
        _get_ciphertext,
        _get_passwords,
        _show_result,
    )

    console = ctx["console"]
    ct = _get_ciphertext(ciphertext)
    passwords = _get_passwords(wordlist)
    aes_mode = AES.MODE_ECB if mode.upper() == "ECB" else AES.MODE_CBC

    for password in passwords:
        key = _derive_behinder_key(password)
        cipher = (
            AES.new(key, aes_mode)
            if aes_mode == AES.MODE_ECB
            else AES.new(key, aes_mode, iv=IV)
        )

        try:
            plaintext = unpad(cipher.decrypt(ct), AES.block_size).decode()
            _show_result(console, password, key, plaintext)
            break
        except UnicodeDecodeError, ValueError:
            continue


@click.command(help="Decrypt Behinder XOR payload with wordlist")
@click.pass_obj
@click.argument("ciphertext", required=False)
@click.option("-w", "--wordlist", type=Path, required=True, help="Wordlist file path")
def xor(ctx: ContextObject, ciphertext: str | None, wordlist: Path) -> None:
    from itertools import cycle

    from quas.behinder.common import (
        _derive_behinder_key,
        _get_ciphertext,
        _get_passwords,
        _show_result,
    )

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


app.add_command(aes)
app.add_command(xor)
