from pathlib import Path

import click

from quas.context import ContextObject


@click.group(help="Utility tools")
def app() -> None: ...


@click.command(help="Reverse bytes of a file")
@click.pass_obj
@click.argument("infile", type=Path)
@click.argument(
    "outfile",
    type=Path,
    default="-",
)
def rev(ctx: ContextObject, infile: Path, outfile: Path) -> None:
    import subprocess

    data = bytes(reversed(infile.read_bytes()))
    if outfile == Path("-"):
        _ = subprocess.run(["hexyl"], input=data)
    else:
        _ = outfile.write_bytes(data)


app.add_command(rev)
