import heapq
from sys import stdin

import click
from rich.table import Table

from quas.context import ContextObject
from quas.crypto.ciphers.columnar import ColumnarCipher
from quas.crypto.crackers import ColumnarCracker


@click.command(help="Crack columnar transposition cipher with quadgram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def crack(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    console = ctx["console"]

    ciphertext = (ciphertext or stdin.read()).strip()
    results = ColumnarCracker().crack(ciphertext.upper())

    table = Table("Cols", "Plaintext", "Score", box=None)
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = ColumnarCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        table.add_row(str(key.cols), plaintext, str(score))
    console.print(table, markup=False)
