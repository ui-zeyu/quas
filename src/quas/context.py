from typing import TypedDict

from rich.console import Console


class ContextObject(TypedDict):
    console: Console
    debug: bool
