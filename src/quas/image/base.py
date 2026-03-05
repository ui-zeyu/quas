from dataclasses import dataclass

from PIL import Image

from quas.core.protocols import CommandResult


@dataclass
class ImageResult(CommandResult[Image.Image]):
    data: Image.Image

    def __rich__(self) -> str:
        return ""
