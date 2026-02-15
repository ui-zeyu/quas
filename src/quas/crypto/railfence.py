import heapq
from sys import stdin

import click
from rich.table import Table

from quas.context import ContextObject
from quas.crypto.ciphers.railfence import RailFenceCipher
from quas.crypto.crackers import RailFenceCracker


@click.command(help="Crack rail fence cipher with quadgram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def crack(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    console = ctx["console"]

    ciphertext = (ciphertext or stdin.read()).strip()
    results = RailFenceCracker().crack(ciphertext.upper())

    table = Table("Rails", "Plaintext", "Score", box=None)
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = RailFenceCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        table.add_row(str(key.rails), plaintext, str(score))
    console.print(table, markup=False)
