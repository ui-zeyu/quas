from pathlib import Path

import click

from quas.context import ContextObject


@click.group(help="PDF analysis tools")
def app() -> None: ...


@click.command(help="Extract and display all PDF streams")
@click.pass_obj
@click.argument("infile", type=Path)
@click.option(
    "-s",
    "--strategy",
    type=click.Choice(["NORMAL", "REGEX"], case_sensitive=False),
    default="NORMAL",
    help="Scanning strategy: normal or regex",
)
def stream(ctx: ContextObject, infile: Path, strategy: str) -> None:
    import magic
    from rich.panel import Panel

    from quas.pdf.stream import MAX_CONTENT_LENGTH, ScanStrategy

    console = ctx["console"]
    strategy_enum = ScanStrategy[strategy.upper()]
    scanner = strategy_enum.to_scanner()

    for objgen, data in scanner.scan(infile, console):
        content = data.decode(errors="replace")
        content_type = magic.from_buffer(data)
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + "..."

        panel = Panel(
            content,
            title=f"[bold cyan]Stream {objgen}[/bold cyan]",
            subtitle=f"[bold cyan]{content_type}[/bold cyan]",
            expand=True,
            highlight=True,
        )
        console.print(panel)


app.add_command(stream)
