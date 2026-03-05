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
    from sys import stdin

    from rich.table import Table

    from quas.crypto.affine import perform_affine_crack

    console = ctx["console"]
    ciphertext = (ciphertext or stdin.read()).strip()

    results = perform_affine_crack(ciphertext, top)

    table = Table("a", "b", "Plaintext", "Score", box=None)
    for res in results:
        table.add_row(str(res.a), str(res.b), res.plaintext, str(res.score))
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
    from sys import stdin

    from rich.panel import Panel
    from rich.table import Table

    from quas.crypto.analyse import perform_analysis

    if hex_flag and b64_flag:
        raise click.BadParameter("Cannot specify both --hex and --base64")
    console = ctx["console"]
    ciphertext = ciphertext if ciphertext is not None else stdin.read()
    if hex_flag:
        ciphertext = bytes.fromhex(ciphertext).decode(errors="ignore")
    elif b64_flag:
        ciphertext = b64decode(ciphertext).decode(errors="ignore")
    ciphertext = ciphertext.strip()

    result = perform_analysis(ciphertext)

    table = Table("Char", "Count", "Percent", "Binary", box=None, expand=True)
    for stat in result.frequencies:
        table.add_row(stat.char, str(stat.count), f"{stat.percent:.2f}%", stat.binary)
    console.print(Panel(table, title="Frequency Analysis"))

    table = Table("Char", "Count", "Percent", "Standard", box=None, expand=True)
    for stat in result.alpha_frequencies:
        standard_str = (
            f"{stat.standard_percent:.2f}%"
            if stat.standard_percent is not None
            else "0.00%"
        )
        table.add_row(stat.char, str(stat.count), f"{stat.percent:.2f}%", standard_str)
    console.print(Panel(table, title="Frequency Analysis (Upper Case)"))

    table = Table("Scorer", "Score", "Length", "Normal Range", box=None, expand=True)
    table.add_row(
        "IoC", f"{result.ioc_score:.3f}", str(result.alpha_length), "0.0567 - 0.0767"
    )
    table.add_row(
        "Quadgram",
        f"{result.quadgram_score:.3f}",
        str(result.alpha_length),
        "10.0 - 11.0",
    )
    console.print(Panel(table, title="Scoring Analysis"))


@click.command(help="Bruteforce caesar cipher with quadgram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def caesar(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    from sys import stdin

    from rich.table import Table

    from quas.crypto.caesar import perform_caesar_crack

    console = ctx["console"]
    ciphertext = (ciphertext or stdin.read()).strip()

    results = perform_caesar_crack(ciphertext, top)

    table = Table("Shift", "Plaintext", "Score", box=None)
    for res in results:
        table.add_row(str(res.shift), res.plaintext, str(res.score))
    console.print(table, markup=False)


@click.command(help="Crack columnar transposition cipher with quadgram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def columnar(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    from sys import stdin

    from rich.table import Table

    from quas.crypto.columnar import perform_columnar_crack

    console = ctx["console"]
    ciphertext = (ciphertext or stdin.read()).strip()

    results = perform_columnar_crack(ciphertext, top)

    table = Table("Cols", "Plaintext", "Score", box=None)
    for res in results:
        table.add_row(str(res.cols), res.plaintext, str(res.score))
    console.print(table, markup=False)


@click.command(help="Crack rail fence cipher with quadgram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def railfence(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    from sys import stdin

    from rich.table import Table

    from quas.crypto.railfence import perform_railfence_crack

    console = ctx["console"]
    ciphertext = (ciphertext or stdin.read()).strip()

    results = perform_railfence_crack(ciphertext, top)

    table = Table("Rails", "Plaintext", "Score", box=None)
    for res in results:
        table.add_row(str(res.rails), res.plaintext, str(res.score))
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
    from sys import stdin

    from rich.table import Table

    from quas.crypto.substitute import perform_sub_crack

    console = ctx["console"]
    ciphertext = (ciphertext or stdin.read()).strip()

    results = perform_sub_crack(ciphertext, calphabet, restarts, top)

    table = Table("Key", "Plaintext", "Score", box=None)
    for res in results:
        table.add_row(res.key, res.plaintext, str(res.score))
    console.print(table, markup=False)


@click.command(help="Crack XOR cipher using frequency analysis")
@click.pass_obj
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
@click.argument("ciphertext", type=str, required=False)
def xor(ctx: ContextObject, top: int, ciphertext: str | None) -> None:
    from sys import stdin

    from rich.table import Table

    from quas.crypto.xor import perform_xor_crack

    console = ctx["console"]
    ciphertext = (ciphertext or stdin.read()).strip()

    results = perform_xor_crack(ciphertext, top)

    table = Table("Key (Hex)", "Plaintext (Bytes)", "Score", box=None)
    for res in results:
        table.add_row(res.key_hex, str(res.plaintext), str(res.score))
    console.print(table, markup=False)


app.add_command(affine)
app.add_command(analyse)
app.add_command(caesar)
app.add_command(columnar)
app.add_command(railfence)
app.add_command(sub)
app.add_command(xor)
