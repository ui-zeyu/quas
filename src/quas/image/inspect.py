from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from rich.table import Table

from quas.core.protocols import CommandResult


@dataclass
class InspectItem:
    index: int
    r: int
    g: int
    b: int
    a: int


@dataclass
class InspectPayload:
    items: list[InspectItem]


@dataclass
class InspectResult(CommandResult[InspectPayload]):
    data: InspectPayload

    def __rich__(self) -> Table:
        table = Table("No.", "RGBA", box=None, highlight=True)
        for item in self.data.items:
            table.add_row(
                str(item.index), f"[ {item.r}, {item.g}, {item.b}, {item.a} ]"
            )
        return table


def perform_inspect(
    infile: Path, x: int, y: int, stepx: int, stepy: int, count: int
) -> InspectResult:
    import numpy as np

    img = Image.open(infile).convert("RGBA")
    arr = np.array(img)
    pixels = arr[y::stepy, x::stepx]
    pixels = pixels.reshape(-1, 4)
    display_pixels = pixels if count == 0 else pixels[:count]

    items = []
    for i, (r, g, b, a) in enumerate(display_pixels):
        items.append(InspectItem(index=i, r=int(r), g=int(g), b=int(b), a=int(a)))

    return InspectResult(InspectPayload(items=items))
