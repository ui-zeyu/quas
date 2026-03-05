from pathlib import Path

import click

from quas.commands.context import ContextObject


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
    from quas.util.rev import perform_rev

    console = ctx["console"]
    result = perform_rev(infile, outfile)
    result.save_or_show()
    console.print(result)


app.add_command(rev)
