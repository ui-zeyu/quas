import importlib
import logging
import pkgutil
from importlib import metadata
from typing import Annotated

import click
import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install
from typer.core import TyperGroup
from typer.main import get_command

from .context import ContextObject


class LazyGroup(TyperGroup):
    def list_commands(self, ctx: click.Context) -> list[str]:
        import quas.commands

        commands = super().list_commands(ctx)
        for _, name, _ in pkgutil.iter_modules(quas.commands.__path__):
            commands.append(name)
        return sorted(commands)

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        if cmd := super().get_command(ctx, cmd_name):
            return cmd

        try:
            module = importlib.import_module(f"quas.commands.{cmd_name}")
            return get_command(module.app)
        except ImportError, AttributeError:
            return None


app = typer.Typer(
    cls=LazyGroup,
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


@app.command(help="Show the version of Quas")
def version(ctx: typer.Context) -> None:
    ctx.obj["console"].print(metadata.version("quas"))
