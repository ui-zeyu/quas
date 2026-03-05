from typing import Protocol

from rich.console import RenderableType


class CommandResult[T](Protocol):
    data: T

    def __rich__(self) -> RenderableType: ...
