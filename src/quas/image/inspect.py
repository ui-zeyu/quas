from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from rich.console import Group
from rich.panel import Panel
from rich.table import Table


@dataclass
class InspectPayload:
    path: Path
    pixels: Sequence[tuple[int, int, tuple[int, ...]]]

    def __rich__(self) -> Group:
        table = Table(title=f"Pixels from {self.path.name}")
        table.add_column("X", justify="right", style="cyan")
        table.add_column("Y", justify="right", style="cyan")
        table.add_column("RGBA", justify="center", style="green")

        for x, y, rgba in self.pixels:
            table.add_row(str(x), str(y), str(rgba))

        return Group(Panel(table, expand=False))


def perform_inspect(
    infile: Path,
    x: int,
    y: int,
    stepx: int,
    stepy: int,
    count: int,
) -> InspectPayload:
    image = Image.open(infile)
    width, height = image.size
    pixels = []
    c = 0
    for i in range(y, height, stepy):
        for j in range(x, width, stepx):
            if count != 0 and c >= count:
                break
            pixels.append((j, i, image.getpixel((j, i))))
            c += 1
        if count != 0 and c >= count:
            break
    return InspectPayload(infile, pixels)
