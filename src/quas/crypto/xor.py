import heapq
from sys import stdin

import click
from rich.table import Table

from quas.context import ContextObject
from quas.crypto.ciphers import XorCipher
from quas.crypto.crackers import XorCracker


@click.command(help="Crack XOR cipher using frequency analysis")
@click.pass_obj
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
@click.argument("ciphertext", type=str, required=False)
def crack(ctx: ContextObject, top: int, ciphertext: str | None) -> None:
    console = ctx["console"]

    ciphertext = (ciphertext or stdin.read()).strip()
    ciphertext: bytes = bytes.fromhex(ciphertext)
    results = XorCracker().crack(ciphertext)

    table = Table("Key (Hex)", "Plaintext (Bytes)", "Score", box=None)
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = XorCipher(key)
        plaintext = cipher.decrypt(ciphertext)
        table.add_row(key.value.hex(), str(plaintext), str(score))
    console.print(table, markup=False)
