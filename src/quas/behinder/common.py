import sys
from base64 import b64decode
from collections.abc import Sequence
from hashlib import md5
from pathlib import Path

from Cryptodome.Cipher import AES

IV = b"\x00" * AES.block_size
MAX_PLAINTEXT_DISPLAY = 60


def _get_ciphertext(ciphertext: str | None) -> bytes:
    ciphertext = sys.stdin.read() if ciphertext is None else ciphertext
    return b64decode(ciphertext.strip())


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
