from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from quas.core import UseCase
from quas.pdf.stream import ScanStrategy

if TYPE_CHECKING:
    from quas.pdf.stream import StreamPayload

app = typer.Typer(name="pdf", help="PDF analysis tools", no_args_is_help=True)


@app.callback()
def callback() -> None: ...


@dataclass(kw_only=True)
class StreamUseCase(UseCase["StreamPayload"]):
    """Extract and display all PDF streams."""

    GROUP = app
    COMMAND = "stream"

    infile: Annotated[Path, typer.Argument(help="Input PDF file")]
    strategy: Annotated[
        ScanStrategy,
        typer.Option(
            "--strategy",
            "-s",
            help="Scanning strategy: normal or regex",
        ),
    ] = ScanStrategy.NORMAL

    def execute(self) -> StreamPayload:
        console = self.ctx.obj["console"]
        return ScanStrategy.perform_scan(self.infile, self.strategy, console)

    def effect(self, result: StreamPayload) -> None:
        self.ctx.obj["console"].print(result)
