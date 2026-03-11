from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Annotated

import typer
from Cryptodome.Util.number import long_to_bytes
from gmpy2 import mpz

from quas.core import UseCase
from quas.rsa import dispatcher
from quas.rsa.base import RSAPayload

app = typer.Typer(
    name="rsa",
    help="RSA decryption and analysis tool",
    no_args_is_help=True,
)


@app.callback()
def callback() -> None: ...


@dataclass(kw_only=True)
class RsaUseCase(UseCase[Iterator[RSAPayload]]):
    """RSA decryption and analysis tool."""

    GROUP = app
    COMMAND = "rsa"

    ns: Annotated[list[str], typer.Option("--ns", "-n", help="Modulus N")] = field(
        default_factory=list
    )
    es: Annotated[list[str], typer.Option("--es", "-e", help="Public exponent E")] = (
        field(default_factory=list)
    )
    cs: Annotated[list[str], typer.Option("--cs", "-c", help="Ciphertext C")] = field(
        default_factory=list
    )
    p: Annotated[str | None, typer.Option("-p", help="Prime factor P")] = None
    q: Annotated[str | None, typer.Option("-q", help="Prime factor Q")] = None
    d: Annotated[str | None, typer.Option("-d", help="Private key D")] = None
    dp: Annotated[str | None, typer.Option("-dp", help="Private key component dp")] = (
        None
    )
    dq: Annotated[str | None, typer.Option("-dq", help="Private key component dq")] = (
        None
    )
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Iteration limit"),
    ] = 1_000_000

    def execute(self) -> Iterator[RSAPayload]:
        ns = [mpz(x) for x in self.ns]
        es = [mpz(x) for x in self.es]
        cs = [mpz(x) for x in self.cs]
        p = mpz(self.p) if self.p else None
        q = mpz(self.q) if self.q else None
        d = mpz(self.d) if self.d else None
        dp = mpz(self.dp) if self.dp else None
        dq = mpz(self.dq) if self.dq else None

        with self.ctx.obj["console"].status("Starting analysis...") as status:
            for m in dispatcher(
                ns,
                es,
                cs,
                p,
                q,
                d,
                dp,
                dq,
                self.limit,
                status,
            ):
                plaintext = long_to_bytes(int(m)).decode(errors="replace")
                yield RSAPayload(
                    m=int(m), plaintext=plaintext, status=str(status.status)
                )

    def effect(self, result: Iterator[RSAPayload]) -> None:
        for payload in result:
            self.ctx.obj["console"].print(payload)
