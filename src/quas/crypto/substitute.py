import heapq
import string
from sys import stdin

import click
from rich.table import Table

from quas.analysis.alphabet import Alphabet
from quas.context import ContextObject
from quas.crypto.ciphers.substitute import SubstitutionCipher
from quas.crypto.crackers import SubstituteCracker


@click.command(help="Crack substitution cipher using hill climbing with N-gram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option(
    "-c",
    "--calphabet",
    type=str,
    default=string.ascii_uppercase,
    help="Cipher alphabet",
)
@click.option(
    "-r",
    "--restarts",
    type=int,
    default=100,
    help="Number of hill climbing restarts",
)
@click.option("-t", "--top", type=int, default=3, help="Show top N results")
def crack(
    ctx: ContextObject,
    ciphertext: str | None,
    calphabet: str,
    restarts: int,
    top: int,
) -> None:
    console = ctx["console"]

    calphabet: list[str] = calphabet.split() if " " in calphabet else list(calphabet)
    calphabet: Alphabet = Alphabet(calphabet)

    ciphertext = (ciphertext or stdin.read()).strip().upper()
    cindices = calphabet.encode(ciphertext)
    results = SubstituteCracker(calphabet, restarts).crack(cindices)

    table = Table("Key", "Plaintext", "Score", box=None)
    for key, score in heapq.nlargest(top, set(results), lambda x: x.score):
        cipher = SubstitutionCipher(calphabet, key)
        plaintext = cipher.decrypt_str(ciphertext)
        table.add_row(cipher.palphabet().decode(key), plaintext, str(score))
    console.print(table, markup=False)
