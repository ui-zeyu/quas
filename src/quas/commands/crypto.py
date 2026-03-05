import click

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


@click.group(help="Cryptographic ciphers and crackers")
def app() -> None: ...


@click.command(help="Bruteforce affine cipher with N-gram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def affine(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    import heapq
    from sys import stdin

    from rich.table import Table

    from quas.analysis import english_upper
    from quas.crypto.ciphers import AffineCipher
    from quas.crypto.crackers import AffineCracker

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


@click.command(help="Analyze ciphertext statistics using various scoring methods")
@click.pass_obj
@click.option(
    "--hex", "hex_flag", is_flag=True, help="Input is hex-encoded, decode first"
)
@click.option(
    "--base64", "b64_flag", is_flag=True, help="Input is base64-encoded, decode first"
)
@click.argument("ciphertext", type=str, required=False)
def analyse(
    ctx: ContextObject, hex_flag: bool, b64_flag: bool, ciphertext: str | None
) -> None:
    from base64 import b64decode
    from collections import Counter
    from sys import stdin

    import numpy as np
    from rich.panel import Panel
    from rich.table import Table

    from quas.analysis import english_upper
    from quas.analysis.ioc import IndexOfCoincidence
    from quas.analysis.quadgram import quadgram

    if hex_flag and b64_flag:
        raise click.BadParameter("Cannot specify both --hex and --base64")
    console = ctx["console"]
    ciphertext = ciphertext if ciphertext is not None else stdin.read()
    if hex_flag:
        ciphertext = bytes.fromhex(ciphertext).decode(errors="ignore")
    elif b64_flag:
        ciphertext = b64decode(ciphertext).decode(errors="ignore")
    ciphertext = ciphertext.strip()

    table = Table("Char", "Count", "Percent", "Binary", box=None, expand=True)
    for char, count in Counter(ciphertext).most_common():
        percent = count / len(ciphertext) * 100
        table.add_row(char, str(count), f"{percent:.2f}%", f"{ord(char):08b}")
    console.print(Panel(table, title="Frequency Analysis"))

    alpha_text = "".join(x for x in ciphertext if x.isalpha()).upper()
    table = Table("Char", "Count", "Percent", "Standard", box=None, expand=True)
    for char, count in Counter(alpha_text).most_common():
        percent = count / len(alpha_text) * 100
        standard = STANDARD_FREQUENCY.get(char, 0.0)
        table.add_row(char, str(count), f"{percent:.2f}%", f"{standard:.2f}%")
    console.print(Panel(table, title="Frequency Analysis (Upper Case)"))

    indices = np.array(english_upper.encode(alpha_text), dtype=np.uint32)
    score_ioc = IndexOfCoincidence().score(indices)
    score_quadgram = quadgram.score(indices)

    table = Table("Scorer", "Score", "Length", "Normal Range", box=None, expand=True)
    table.add_row("IoC", f"{score_ioc:.3f}", str(indices.size), "0.0567 - 0.0767")
    table.add_row("Quadgram", f"{score_quadgram:.3f}", str(indices.size), "10.0 - 11.0")
    console.print(Panel(table, title="Scoring Analysis"))


@click.command(help="Bruteforce caesar cipher with quadgram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def caesar(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    import heapq
    from sys import stdin

    from rich.table import Table

    from quas.analysis import english_upper
    from quas.crypto.ciphers import CaesarCipher
    from quas.crypto.crackers import CaesarCracker

    console = ctx["console"]
    ciphertext = (ciphertext or stdin.read()).strip()
    cindices = english_upper.encode(ciphertext.upper())
    results = CaesarCracker().crack(cindices)

    table = Table("Shift", "Plaintext", "Score", box=None)
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = CaesarCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        table.add_row(str(key.value), plaintext, str(score))
    console.print(table, markup=False)


@click.command(help="Crack columnar transposition cipher with quadgram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def columnar(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    import heapq
    from sys import stdin

    from rich.table import Table

    from quas.crypto.ciphers import ColumnarCipher
    from quas.crypto.crackers import ColumnarCracker

    console = ctx["console"]
    ciphertext = (ciphertext or stdin.read()).strip()
    results = ColumnarCracker().crack(ciphertext.upper())

    table = Table("Cols", "Plaintext", "Score", box=None)
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = ColumnarCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        table.add_row(str(key.cols), plaintext, str(score))
    console.print(table, markup=False)


@click.command(help="Crack rail fence cipher with quadgram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def railfence(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    import heapq
    from sys import stdin

    from rich.table import Table

    from quas.crypto.ciphers import RailFenceCipher
    from quas.crypto.crackers import RailFenceCracker

    console = ctx["console"]
    ciphertext = (ciphertext or stdin.read()).strip()
    results = RailFenceCracker().crack(ciphertext.upper())

    table = Table("Rails", "Plaintext", "Score", box=None)
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = RailFenceCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        table.add_row(str(key.rails), plaintext, str(score))
    console.print(table, markup=False)


@click.command(help="Crack substitution cipher using hill climbing with N-gram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option(
    "-c",
    "--calphabet",
    type=str,
    default="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    help="Cipher alphabet",
)
@click.option(
    "-r", "--restarts", type=int, default=100, help="Number of hill climbing restarts"
)
@click.option("-t", "--top", type=int, default=3, help="Show top N results")
def sub(
    ctx: ContextObject, ciphertext: str | None, calphabet: str, restarts: int, top: int
) -> None:
    import heapq
    from sys import stdin

    from rich.table import Table

    from quas.analysis.alphabet import Alphabet
    from quas.crypto.ciphers import SubstitutionCipher
    from quas.crypto.crackers import SubstituteCracker

    console = ctx["console"]
    calphabet_list = calphabet.split() if " " in calphabet else list(calphabet)
    alphabet_obj = Alphabet(calphabet_list)
    ciphertext = (ciphertext or stdin.read()).strip().upper()
    cindices = alphabet_obj.encode(ciphertext)
    results = SubstituteCracker(alphabet_obj, restarts).crack(cindices)

    table = Table("Key", "Plaintext", "Score", box=None)
    for key, score in heapq.nlargest(top, set(results), lambda x: x.score):
        cipher = SubstitutionCipher(alphabet_obj, key)
        plaintext = cipher.decrypt_str(ciphertext)
        table.add_row(cipher.palphabet().decode(key), plaintext, str(score))
    console.print(table, markup=False)


@click.command(help="Crack XOR cipher using frequency analysis")
@click.pass_obj
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
@click.argument("ciphertext", type=str, required=False)
def xor(ctx: ContextObject, top: int, ciphertext: str | None) -> None:
    import heapq
    from sys import stdin

    from rich.table import Table

    from quas.crypto.ciphers import XorCipher
    from quas.crypto.crackers import XorCracker

    console = ctx["console"]
    ciphertext = (ciphertext or stdin.read()).strip()
    ciphertext_bytes = bytes.fromhex(ciphertext)
    results = XorCracker().crack(ciphertext_bytes)

    table = Table("Key (Hex)", "Plaintext (Bytes)", "Score", box=None)
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = XorCipher(key)
        plaintext = cipher.decrypt(ciphertext_bytes)
        table.add_row(key.value.hex(), str(plaintext), str(score))
    console.print(table, markup=False)


app.add_command(affine)
app.add_command(analyse)
app.add_command(caesar)
app.add_command(columnar)
app.add_command(railfence)
app.add_command(sub)
app.add_command(xor)
