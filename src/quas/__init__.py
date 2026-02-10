import logging

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

from quas import behinder, crc, crypto, image, pdf, steg, util
from quas.context import ContextObject

CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    show_default=True,
)


@click.group(
    context_settings=CONTEXT_SETTINGS,
    help="Quas - Steganography and cryptanalysis CLI toolkit",
)
@click.version_option(message="%(prog)s %(version)s")
@click.pass_context
@click.option("-v", "verbose", count=True, help="Increase verbosity level")
@click.option("-d", "--debug", is_flag=True, help="Enable debug mode")
def app(ctx: click.Context, verbose: int, debug: bool) -> None:
    console = Console()

    level = {
        0: logging.WARN,
        1: logging.INFO,
        2: logging.DEBUG,
    }.get(verbose, logging.DEBUG)
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )
    install(console=console, show_locals=True, suppress=[click])

    ctx.obj = ContextObject(console=console, debug=debug)


def main() -> None:
    for module in (steg, util, image, crc, behinder, pdf, crypto):
        app.add_command(module.app, module.__name__.rsplit(".", 1)[-1])
    app()


if __name__ == "__main__":
    main()
