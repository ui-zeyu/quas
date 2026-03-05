from pathlib import Path

import click

from quas.commands.context import ContextObject
from quas.pdf.stream import ScanStrategy


@click.group(help="PDF analysis tools")
def app() -> None: ...


@click.command(help="Extract and display all PDF streams")
@click.pass_obj
@click.argument("infile", type=Path)
@click.option(
    "-s",
    "--strategy",
    type=click.Choice(ScanStrategy, case_sensitive=False),
    default=ScanStrategy.NORMAL,
    help="Scanning strategy: normal or regex",
)
def stream(ctx: ContextObject, infile: Path, strategy: ScanStrategy) -> None:
    console = ctx["console"]
    result = ScanStrategy.perform_scan(infile, strategy, console)
    console.print(result)


app.add_command(stream)
