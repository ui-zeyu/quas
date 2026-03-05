from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from rich.text import Text

from quas.core.protocols import CommandResult


@dataclass
class ImagePayload:
    image: Image.Image
    outfile: Path | None


@dataclass
class ImageResult(CommandResult[ImagePayload]):
    data: ImagePayload

    def __rich__(self) -> Text:
        if self.data.outfile:
            return Text(f"Image saved to {self.data.outfile}", style="green")
        return Text("Image displayed.", style="green")

    def save_or_show(self) -> None:
        if self.data.outfile:
            self.data.image.save(self.data.outfile)
        else:
            self.data.image.show()
