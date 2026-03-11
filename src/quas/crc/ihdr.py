from dataclasses import dataclass
from struct import pack, unpack
from zlib import crc32

from PIL import Image
from rich.console import Group
from rich.panel import Panel

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
IHDR_CHUNK_TYPE = b"IHDR"
MAX_DIMENSION = 5000


@dataclass
class IHDRPayload:
    width: int
    height: int
    image: Image.Image

    def __rich__(self) -> Group:
        return Group(
            Panel(
                f"[bold green]Recovered dimensions:[/bold green]\n"
                f"[cyan]Width:[/cyan] {self.width}\n"
                f"[cyan]Height:[/cyan] {self.height}",
                title="IHDR Recovery Result",
            )
        )


def crack(data: bytes, max_width: int, max_height: int) -> IHDRPayload | None:
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("Invalid PNG signature")

    # Locate IHDR chunk
    ihdr_start = data.find(IHDR_CHUNK_TYPE)
    if ihdr_start == -1:
        raise ValueError("IHDR chunk not found")

    # The IHDR chunk layout:
    # Length (4 bytes), Type (4 bytes), Data (13 bytes), CRC (4 bytes)
    # The CRC is calculated over Type + Data.

    # Original data components
    # data[ihdr_start-4 : ihdr_start] is the length (should be 13)
    # data[ihdr_start : ihdr_start+4] is "IHDR"
    # data[ihdr_start+4 : ihdr_start+4+13] is the 13-byte IHDR data
    # data[ihdr_start+17 : ihdr_start+21] is the original CRC

    ihdr_data = data[ihdr_start + 4 : ihdr_start + 17]
    original_crc = unpack(">I", data[ihdr_start + 17 : ihdr_start + 21])[0]

    # IHDR Data: Width (4), Height (4), Bit depth (1), Color type (1),
    # Compression (1), Filter (1), Interlace (1)
    # We want to bruteforce Width and Height.

    fixed_data = ihdr_data[8:]  # The 5 bytes after width and height

    for w in range(1, max_width + 1):
        for h in range(1, max_height + 1):
            test_data = IHDR_CHUNK_TYPE + pack(">II", w, h) + fixed_data
            if crc32(test_data) == original_crc:
                # Found it! Reconstruct the image for the user.
                # Note: This is just for demonstration, in a real scenario
                # we might want to return the modified data.
                import io

                new_data = (
                    data[: ihdr_start + 4]
                    + pack(">II", w, h)
                    + fixed_data
                    + data[ihdr_start + 17 :]
                )
                image = Image.open(io.BytesIO(new_data))
                return IHDRPayload(w, h, image)
    return None
