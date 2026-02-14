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

STANDARD_FREQUENCY: dict[str, float] = {
    "E": 12.7,
    "T": 9.1,
    "A": 8.2,
    "O": 7.5,
    "I": 7.0,
    "N": 6.7,
    "S": 6.3,
    "H": 6.1,
    "R": 6.0,
    "D": 4.3,
    "L": 4.0,
    "C": 2.8,
    "U": 2.8,
    "M": 2.4,
    "W": 2.4,
    "F": 2.2,
    "G": 2.0,
    "Y": 2.0,
    "P": 1.9,
    "B": 1.5,
    "V": 1.0,
    "K": 0.8,
    "J": 0.15,
    "X": 0.15,
    "Q": 0.10,
    "Z": 0.07,
}


@click.command(help="Analyze ciphertext statistics using various scoring methods")
@click.pass_obj
@click.option("--hex", "hex", is_flag=True, help="Input is hex-encoded, decode first")
@click.option(
    "--base64",
    "base64",
    is_flag=True,
    help="Input is base64-encoded, decode first",
)
@click.argument("ciphertext", type=str, required=False)
def analyse(
    ctx: ContextObject,
    hex: bool,
    base64: bool,
    ciphertext: str | None,
) -> None:
    if hex and base64:
        raise click.BadParameter("Cannot specify both --hex and --base64")
    console = ctx["console"]

    ciphertext = ciphertext if ciphertext is not None else stdin.read()
    if hex:
        ciphertext = bytes.fromhex(ciphertext).decode(errors="ignore")
    elif base64:
        ciphertext = b64decode(ciphertext).decode(errors="ignore")
    ciphertext = ciphertext.strip()

    table = Table("Char", "Count", "Percent", box=None, expand=True)
    for char, count in Counter(ciphertext).most_common():
        percent = count / len(ciphertext) * 100
        table.add_row(char, str(count), f"{percent:.2f}%")
    console.print(Panel(table, title="Frequency Analysis"))

    ciphertext = "".join(x for x in ciphertext if x.isalpha()).upper()
    table = Table("Char", "Count", "Percent", "Standard", box=None, expand=True)
    for char, count in Counter(ciphertext).most_common():
        percent = count / len(ciphertext) * 100
        standard = STANDARD_FREQUENCY.get(char, 0.0)
        table.add_row(char, str(count), f"{percent:.2f}%", f"{standard:.2f}%")
    console.print(Panel(table, title="Frequency Analysis (Upper Case)"))

    indices = np.array(english_upper.encode(ciphertext), dtype=np.uint32)
    score_ioc = IndexOfCoincidence().score(indices)
    score_quadgram = quadgram.score(indices)

    table = Table("Scorer", "Score", "Length", "Normal Range", box=None, expand=True)
    table.add_row("IoC", f"{score_ioc:.3f}", str(indices.size), "0.0567 - 0.0767")
    table.add_row("Quadgram", f"{score_quadgram:.3f}", str(indices.size), "10.0 - 11.0")
    console.print(Panel(table, title="Scoring Analysis"))
