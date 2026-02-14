from base64 import b64decode
from collections import Counter
from sys import stdin

import click
import numpy as np
from rich.panel import Panel
from rich.table import Table

from quas.analysis import english_upper
from quas.analysis.ioc import IndexOfCoincidence
from quas.analysis.quadgram import quadgram
from quas.context import ContextObject


@click.command(help="Analyze ciphertext statistics using various scoring methods")
@click.pass_obj
@click.option("--hex", "hex", is_flag=True, help="Input is hex-encoded, decode first")
@click.option(
    "--base64",
    "base64",
    is_flag=True,
    help="Input is base64-encoded, decode first",
)
@click.argument("text", type=str, required=False)
def analyse(ctx: ContextObject, hex: bool, base64: bool, text: str | None) -> None:
    if hex and base64:
        raise click.BadParameter("Cannot specify both --hex and --base64")
    console = ctx["console"]

    text = text if text is not None else stdin.read()
    if hex:
        text = bytes.fromhex(text).decode(errors="ignore")
    elif base64:
        text = b64decode(text).decode(errors="ignore")
    text = text.strip()

    table = Table("Char", "Count", "Percent", box=None, expand=True)
    for char, count in Counter(text).most_common():
        percent = count / len(text) * 100
        table.add_row(char, str(count), f"{percent:.2f}%")
    console.print(Panel(table, title="Frequency Analysis"))

    indices = np.array(english_upper.encode(text.upper()), dtype=np.uint32)
    quadgram_score = quadgram.score(indices)
    ioc_score = IndexOfCoincidence().score(indices)

    table = Table("Scorer", "Score", "Length", "Normal Range", box=None, expand=True)
    table.add_row("Quadgram", f"{quadgram_score:.3f}", str(indices.size), "10.0 - 11.0")
    table.add_row("IoC", f"{ioc_score:.3f}", str(indices.size), "0.0567 - 0.0767")
    console.print(Panel(table, title="Scoring Analysis"))
