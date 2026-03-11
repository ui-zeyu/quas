from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer

from quas.core import UseCase

app = typer.Typer(name="util", help="Utility commands", no_args_is_help=True)


@app.callback()
def callback() -> None: ...


@dataclass(kw_only=True)
class RevUseCase(UseCase[bytes]):
    """Reverse bytes of a file."""

    GROUP = app
    COMMAND = "rev"

    infile: Annotated[Path, typer.Argument(help="Input file")]
    outfile: Annotated[Path, typer.Option(help="Output file")] = Path("-")

    def execute(self) -> bytes:
        from quas.util.rev import rev

        return rev(self.infile)

    def effect(self, result: bytes) -> None:
        import subprocess

        if self.outfile == Path("-"):
            subprocess.run(["hexyl"], input=result)
        else:
            self.outfile.write_bytes(result)
            self.ctx.obj["console"].print(f"Successfully wrote to {self.outfile}")
