import heapq
from sys import stdin

import click
from rich.table import Table

from quas.analysis import english_upper
from quas.context import ContextObject
from quas.crypto.ciphers import AffineCipher
from quas.crypto.crackers import AffineCracker


@click.command(help="Bruteforce affine cipher with N-gram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def crack(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    console = ctx["console"]

    ciphertext = (ciphertext or stdin.read()).strip()
    cindices = english_upper.encode(ciphertext.upper())
    results = AffineCracker().crack(cindices)

    table = Table("a", "b", "Plaintext", "Score", box=None)
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = AffineCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        table.add_row(str(key.a), str(key.b), plaintext, str(score))
    console.print(table, markup=False)
