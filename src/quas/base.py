from typing import TypedDict

from rich.console import Console

CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    show_default=True,
)


class ContextObject(TypedDict):
    console: Console
    debug: bool
