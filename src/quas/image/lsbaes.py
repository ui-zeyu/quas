from collections.abc import Sequence
from dataclasses import dataclass
from multiprocessing import Pool
from pathlib import Path

from PIL import Image
from rich.console import Console, Group
from rich.panel import Panel

from quas.behinder.aes import Mode, decrypt


@dataclass
class LsbAesPayload:
    path: Path
    password: str
    key: bytes
    data: bytes

    def __rich__(self) -> Group:
        return Group(
            Panel(
                f"[bold green]Password found![/bold green]\n"
                f"[cyan]Password:[/cyan] {self.password}\n"
                f"[cyan]Key:[/cyan] {self.key.hex()}\n"
                f"[cyan]Payload:[/cyan] {self.data.decode(errors='replace')}",
                title=f"LSB AES from {self.path.name}",
            )
        )


def _worker(args: tuple[bytes, Sequence[bytes]]) -> tuple[str, bytes] | None:
    chunk, passwords = args
    if result := decrypt(chunk, passwords, Mode.CBC):
        return result.password.decode(), result.key
    return None


def perform_lsbaes(
    image_path: Path,
    wordlist_path: Path,
    workers: int,
    console: Console,
) -> LsbAesPayload | None:
    image = Image.open(image_path)
    width, height = image.size
    pixels = list(image.getdata())  # type: ignore

    # Extract LSB bits
    bits = ""
    for pixel in pixels:
        for channel in pixel[:3]:
            bits += str(channel & 1)

    # Convert bits to bytes
    data = bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))

    # Load wordlist
    passwords = wordlist_path.read_bytes().splitlines()
    chunk_size = (len(passwords) + workers - 1) // workers
    chunks = [
        passwords[i : i + chunk_size] for i in range(0, len(passwords), chunk_size)
    ]

    with Pool(workers) as pool:
        results = pool.map(_worker, [(data, chunk) for chunk in chunks])

    for result in results:
        if result:
            password, key = result
            return LsbAesPayload(image_path, password, key, data)

    return None
