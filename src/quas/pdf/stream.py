from pathlib import Path

import click
import magic
import pikepdf
from rich.panel import Panel

from quas.context import ContextObject

MAX_CONTENT_LENGTH = 1000


@click.command(help="Extract and display all PDF streams")
@click.pass_obj
@click.argument("infile", type=Path)
def stream(ctx: ContextObject, infile: Path) -> None:
    console = ctx["console"]

    doc = pikepdf.Pdf.open(infile)
    for obj in doc.objects:
        if not isinstance(obj, pikepdf.Stream):
            continue

        data = obj.read_bytes()
        subtitle = magic.from_buffer(data)
        content = data.decode(errors="replace")
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + "..."
        panel = Panel(
            content,
            title=f"[bold cyan]Stream {obj.objgen}[/bold cyan]",
            subtitle=f"[bold cyan]{subtitle}[/bold cyan]",
            expand=True,
            highlight=True,
        )
        console.print(panel)
