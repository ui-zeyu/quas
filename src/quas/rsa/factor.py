from collections.abc import Iterable
from itertools import count, islice
from typing import cast

from gmpy2 import gcd, iroot, mpz, powmod


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
