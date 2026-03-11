from dataclasses import dataclass
from hashlib import md5

from Cryptodome.Cipher import AES
from rich.console import Group
from rich.text import Text

MAX_PLAINTEXT_DISPLAY = 60
IV = b"\x00" * AES.block_size


def _truncate_plaintext(plaintext: str) -> str:
    return (
        plaintext[:MAX_PLAINTEXT_DISPLAY] + "..."
        if len(plaintext) > MAX_PLAINTEXT_DISPLAY
        else plaintext
    )


@dataclass(frozen=True)
class BehinderPayload:
    password: bytes
    key: bytes
    plaintext: str

    def __rich__(self) -> Group:
        return Group(
            Text.from_markup(
                f"[bold cyan]Password:[/bold cyan] {self.password.decode()}"
            ),
            Text.from_markup(f"[bold magenta]Key:[/bold magenta] {self.key!r}"),
            Text.from_markup(
                f"[bold green]Plaintext:[/bold green] {_truncate_plaintext(self.plaintext)}"
            ),
        )


def derive_behinder_key(password: bytes) -> bytes:
    return md5(password).digest()[:16]
