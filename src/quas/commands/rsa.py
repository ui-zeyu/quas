from collections.abc import Sequence

import click
from gmpy2 import mpz

from quas.commands.context import ContextObject


@click.command(help="RSA decryption and analysis tool")
@click.pass_obj
@click.option("-n", "ns", multiple=True, type=mpz, help="Modulus N")
@click.option("-e", "es", multiple=True, type=mpz, help="Public exponent E")
@click.option("-c", "cs", multiple=True, type=mpz, help="Ciphertext C")
@click.option("-p", type=mpz, help="Prime factor P")
@click.option("-q", type=mpz, help="Prime factor Q")
@click.option("-d", type=mpz, help="Private key D")
@click.option("-dp", type=mpz, help="Private key component dp")
@click.option("-dq", type=mpz, help="Private key component dq")
@click.option("-l", "--limit", type=int, default=1_000_000, help="Iteration limit")
def app(
    ctx: ContextObject,
    ns: Sequence[mpz],
    es: Sequence[mpz],
    cs: Sequence[mpz],
    p: mpz | None,
    q: mpz | None,
    d: mpz | None,
    dp: mpz | None,
    dq: mpz | None,
    limit: int,
) -> None:
    from Cryptodome.Util.number import long_to_bytes

    from quas.rsa import dispatcher
    from quas.rsa.base import RSAPayload, RSAResult

    console = ctx["console"]

    with console.status("Starting analysis...") as status:
        for m in dispatcher(ns, es, cs, p, q, d, dp, dq, limit, status):
            plaintext = long_to_bytes(int(m)).decode(errors="replace")
            result = RSAResult(
                RSAPayload(m=int(m), plaintext=plaintext, status=str(status.status))
            )
            console.print(result)
