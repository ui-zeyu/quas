from collections.abc import Iterable

from gmpy2 import gcdext, invert, iroot, is_square, mpz, powmod


def small_e(n: mpz, e: mpz, c: mpz, limit: int) -> mpz | None:
    for k in range(limit):
        cc = c + mpz(k) * n
        m, exact = iroot(cc, e)
        if exact:
            return m
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
