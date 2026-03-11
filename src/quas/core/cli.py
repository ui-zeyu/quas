import importlib
import logging
import pkgutil
from importlib import metadata
from typing import Annotated

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

import quas.commands

from .context import ContextObject

app = typer.Typer(
    help="Quas - Steganography and cryptanalysis CLI toolkit",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


@app.callback()
def callback(
    ctx: typer.Context,
    verbose: Annotated[
        int,
        typer.Option(
            "-v",
            "--verbose",
            count=True,
            help="Increase verbosity level",
        ),
    ] = 0,
    debug: Annotated[
        bool,
        typer.Option(
            "-d",
            "--debug",
            help="Enable debug mode",
        ),
    ] = False,
) -> None:
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
    install(console=console, show_locals=True, suppress=[typer])

    ctx.obj = ContextObject(console=console, debug=debug)


@app.command()
def version(ctx: typer.Context) -> None:
    ctx.obj["console"].print(metadata.version("quas"))


def main() -> None:
    for _, module_name, _ in pkgutil.iter_modules(quas.commands.__path__):
        module = importlib.import_module(f"quas.commands.{module_name}")
        app.add_typer(module.app, name=module_name)
    app()
