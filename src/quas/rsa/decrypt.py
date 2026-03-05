from gmpy2 import invert, iroot, mpz, powmod


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
    return None
