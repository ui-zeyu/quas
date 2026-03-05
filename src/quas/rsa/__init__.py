from collections.abc import Iterable, Sequence

from gmpy2 import gcd, mpz
from rich.status import Status

from .attacks import common_modulus, hastad_broadcast, rabin, small_e, wiener
from .decrypt import (
    known_d_n,
    known_dp_dq,
    known_dp_or_dq,
    known_p_q_e,
    no_d_small_m,
)
from .factor import factor_fermat, factor_pollard, factor_williams

__all__ = [
    "common_modulus",
    "dispatcher",
    "factor_fermat",
    "factor_pollard",
    "factor_williams",
    "hastad_broadcast",
    "known_d_n",
    "known_dp_dq",
    "known_dp_or_dq",
    "known_p_q_e",
    "no_d_small_m",
    "rabin",
    "small_e",
    "wiener",
]


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

    match ns, es, cs:
        case [n], _, [c] if d is not None:
            status.update("Known d decryption")
            yield known_d_n(d, n, c)
        case [], [e], [c]:
            status.update("Small e attack")
            if e < 256 and (m := small_e(mpz(0), e, c, 1)):
                yield m
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
