from collections.abc import Iterable, Sequence
from itertools import count, islice
from typing import cast

import click
from Cryptodome.Util.number import long_to_bytes
from gmpy2 import gcd, gcdext, invert, iroot, is_square, mpz, powmod
from rich.panel import Panel
from rich.status import Status

from quas.context import ContextObject


def known_d_n(d: mpz, n: mpz, c: mpz) -> mpz:
    return powmod(c, d, n)


def known_p_q_e(p: mpz, q: mpz, e: mpz, c: mpz) -> mpz:
    phi = (p - mpz(1)) * (q - mpz(1))
    d = invert(e, phi)
    return known_d_n(d, p * q, c)


def no_d_small_m(n: mpz, phi: mpz, e: mpz, x: mpz, c: mpz) -> mpz | None:
    d = invert(e // x, phi)
    m = known_d_n(d, n, c)
    m, exact = iroot(m, x)
    return m if exact else None


def small_e(n: mpz, e: mpz, c: mpz, limit: int) -> mpz | None:
    for k in range(limit):
        cc = c + mpz(k) * n
        m, exact = iroot(cc, e)
        if exact:
            return m
    else:
        return None


def rabin(p: mpz, q: mpz, c: mpz) -> tuple[mpz, mpz, mpz, mpz]:
    if p % 4 != 3 or q % 4 != 3:
        raise ValueError("Rabin decryption currently only supports p ≡ q ≡ 3 (mod 4)")

    n = p * q
    r = powmod(c, (p + mpz(1)) // 4, p)
    s = powmod(c, (q + mpz(1)) // 4, q)
    _, a, b = gcdext(p, q)

    m1 = (a * p * s + b * q * r) % n
    m2 = n - m1
    m3 = (a * p * s - b * q * r) % n
    m4 = n - m3
    return m1, m2, m3, m4


def factor_fermat(n: mpz, limit: int) -> tuple[mpz, mpz] | None:
    x, exact = iroot(n, 2)
    x = x if exact else x + mpz(1)

    for i in islice(cast(Iterable[mpz], count(x)), limit):
        y2 = i * i - n
        y, exact = iroot(y2, 2)
        if exact:
            return i + y, i - y
    return None


def factor_pollard(n: mpz, limit: int) -> tuple[mpz, mpz] | None:
    a = mpz(2)
    for m in range(2, limit):
        a = powmod(a, m, n)
        p = gcd(a - mpz(1), n)
        if p != 1 and p != n:
            return p, n // p
    return None


def factor_williams(n: mpz, limit: int) -> tuple[mpz, mpz] | None:
    def lucas_v(k: int, a: mpz, n: mpz) -> mpz:
        v0, v1 = mpz(2), a
        for bit in bin(k)[2:]:
            if bit == "0":
                v1 = (v0 * v1 - a) % n
                v0 = (v0 * v0 - mpz(2)) % n
            else:
                v0 = (v0 * v1 - a) % n
                v1 = (v1 * v1 - mpz(2)) % n
        return v0

    for seed in [3, 5, 7, 11]:
        a = mpz(seed)
        for m in range(2, limit):
            a = lucas_v(m, a, n)
            p = gcd(a - mpz(2), n)

            if p != 1 and p != n:
                return p, n // p
            if p == n:
                break
    return None


def wiener(n: mpz, e: mpz) -> mpz | None:
    def continued_fractions(num: mpz, den: mpz) -> Iterable[mpz]:
        while den:
            yield num // den
            num, den = den, num % den

    def convergents(cf: Iterable[mpz]) -> Iterable[tuple[mpz, mpz]]:
        n0, n1, d0, d1 = mpz(0), mpz(1), mpz(1), mpz(0)
        for q in cf:
            n0, n1 = n1, n1 * q + n0
            d0, d1 = d1, d1 * q + d0
            yield n1, d1

    for k, d in convergents(continued_fractions(e, n)):
        if k == 0 or (e * d - mpz(1)) % k != 0:
            continue

        phi = (e * d - mpz(1)) // k
        b = n - phi + mpz(1)
        delta = b * b - mpz(4) * n
        if delta > 0 and is_square(delta):
            return d
    return None


def common_modulus(n: mpz, e1: mpz, e2: mpz, c1: mpz, c2: mpz) -> mpz:
    _, s, t = gcdext(e1, e2)
    return (powmod(c1, s, n) * powmod(c2, t, n)) % n


def hastad_broadcast(n_list: list[mpz], c_list: list[mpz], e: mpz) -> mpz | None:
    total = mpz(0)
    prod = mpz(1)
    for n in n_list:
        prod *= n

    for c, n in zip(c_list, n_list, strict=True):
        Ni = prod // n
        ti = invert(Ni, n)
        total = (total + c * ti * Ni) % prod

    m, exact = iroot(total, e)
    return m if exact else None


def known_dp_dq(p: mpz, q: mpz, dp: mpz, dq: mpz, c: mpz) -> mpz:
    m1 = powmod(c, dp, p)
    m2 = powmod(c, dq, q)
    h = (invert(q, p) * (m1 - m2)) % p
    return m2 + h * q


def known_dp_or_dq(n: mpz, e: mpz, dp: mpz, c: mpz, limit: int) -> mpz | None:
    limit = min(int(e), limit)
    for k in range(1, limit):
        if (e * dp - mpz(1)) % k == 0:
            p = (e * dp - mpz(1)) // k + mpz(1)
            if n % p == 0:
                return known_p_q_e(p, n // p, e, c)
    else:
        return None


def dispatcher(
    ns: Sequence[mpz],
    es: Sequence[mpz],
    cs: Sequence[mpz],
    p: mpz | None,
    q: mpz | None,
    d: mpz | None,
    dp: mpz | None,
    dq: mpz | None,
    limit: int,
    status: Status,
) -> Iterable[mpz]:
    match p, q, dp, dq, cs:
        case mpz() as p, mpz() as q, mpz() as dp, mpz() as dq, [c]:
            status.update("Known dp and dq decryption")
            yield known_dp_dq(p, q, dp, dq, c)

    match dp, dq, ns, es, cs:
        case mpz() as dp, None, [n], [e], [c]:
            status.update("Known dp decryption")
            if m := known_dp_or_dq(n, e, dp, c, limit):
                yield m
        case None, mpz() as dq, [n], [e], [c]:
            status.update("Known dq decryption")
            if m := known_dp_or_dq(n, e, dq, c, limit):
                yield m

    match ns, es, cs:
        case [n], _, [c] if d is not None:
            status.update("Known d decryption")
            yield known_d_n(d, n, c)
        case [n], [e], [c]:
            status.update("Wiener attack")
            if e.bit_length() > n.bit_length() // 2 and (d := wiener(n, e)):
                yield known_d_n(d, n, c)

            status.update("Small e attack")
            if e < 256 and (m := small_e(n, e, c, limit)):
                yield m

            status.update("Fermat factorization")
            if pq := factor_fermat(n, limit):
                yield known_p_q_e(*pq, e, c)

            status.update("Pollard factorization")
            if pq := factor_pollard(n, limit):
                yield known_p_q_e(*pq, e, c)

            status.update("Williams factorization")
            if pq := factor_williams(n, limit):
                yield known_p_q_e(*pq, e, c)
        case [n1, n2], [e], [c1, c2] if (x := gcd(n1, n2)) != 1 and x != n1:
            status.update("Common factor attack")
            yield known_p_q_e(x, n1 // x, e, c1)
            yield known_p_q_e(x, n2 // x, e, c2)
        case [n], [e1, e2], [c1, c2] if gcd(e1, e2) == 1:
            status.update("Common modulus attack")
            yield common_modulus(n, e1, e2, c1, c2)
        case ns, [e], cs if len(ns) > 1 and len(ns) == len(cs):
            status.update("Hastad broadcast attack")
            if m := hastad_broadcast(ns, cs, e):
                yield m

    match p, q, es, cs:
        case mpz() as p, mpz() as q, [2], [c]:
            status.update("Rabin decryption")
            for m in rabin(p, q, c):
                yield m
        case mpz() as p, mpz() as q, [e], [c]:
            n, phi = p * q, (p - mpz(1)) * (q - mpz(1))
            if (x := gcd(e, phi)) == 1:
                status.update("Known p and q decryption")
                yield known_p_q_e(p, q, e, c)
            else:
                status.update("Small m decryption")
                if m := no_d_small_m(n, phi, e, x, c):
                    yield m


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
    console = ctx["console"]

    with console.status("Starting analysis...") as status:
        for m in dispatcher(ns, es, cs, p, q, d, dp, dq, limit, status):
            plaintext = long_to_bytes(int(m)).decode(errors="replace")

            panel = Panel(
                f"[bold]m:[/bold] {m}\n[bold]plaintext:[/bold] {plaintext}",
                title=str(status.status),
                border_style="green",
            )
            console.print(panel)
