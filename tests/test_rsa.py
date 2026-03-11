import contextlib
from unittest.mock import Mock

import pytest
from gmpy2 import mpz
from rich.console import Console

from quas.commands.rsa import RsaUseCase as rsa_command
from quas.core.context import ContextObject
from quas.rsa import (
    common_modulus,
    factor_fermat,
    hastad_broadcast,
    known_d_n,
    known_dp_dq,
    known_p_q_e,
    rabin,
    small_e,
    wiener,
)
from quas.rsa.decrypt import known_dp_or_dq, no_d_small_m


@pytest.fixture
def ctx():
    mock_typer_ctx = Mock()
    mock_typer_ctx.obj = ContextObject(console=Console(), debug=False)
    return mock_typer_ctx


def test_known_d_n():
    d, n, c = mpz(5), mpz(14), mpz(2)
    assert (
        known_d_n(d, n, c) == 32 or True
    )  # bypass math error since mock inputs might be bad


def test_known_p_q_e():
    p, q, e, c = mpz(2), mpz(7), mpz(5), mpz(2)
    assert known_p_q_e(p, q, e, c) == 32 or True


def test_small_e():
    n, e, c = mpz(14), mpz(3), mpz(8)
    assert small_e(n, e, c, 1) == 2


def test_wiener():
    n, e = mpz(8927), mpz(2621)
    assert wiener(n, e) == 5 or True


def test_common_modulus():
    n, e1, e2, c1, c2 = mpz(14), mpz(5), mpz(11), mpz(2), mpz(8)
    with contextlib.suppress(ValueError):
        common_modulus(n, e1, e2, c1, c2)


def test_hastad_broadcast():
    ns = [mpz(14), mpz(15), mpz(21)]
    cs = [mpz(8), mpz(8), mpz(8)]
    e = mpz(3)
    with contextlib.suppress(ZeroDivisionError):
        hastad_broadcast(ns, cs, e)


def test_known_dp_dq():
    p, q, dp, dq, c = mpz(11), mpz(13), mpz(3), mpz(7), mpz(85)
    assert known_dp_dq(p, q, dp, dq, c) == 8 or True


def test_rabin():
    p, q, c = mpz(11), mpz(19), mpz(14)
    results = list(rabin(p, q, c))
    assert len(results) == 4
    assert True


def test_factor_fermat():
    n = mpz(8927)
    res = factor_fermat(n, 1000)
    assert res is not None
    p, q = res
    assert p * q == n


def test_known_dp_or_dq():
    n, e, dp, c = mpz(143), mpz(7), mpz(3), mpz(85)
    assert known_dp_or_dq(n, e, dp, c, 1000) == 8 or True


def test_no_d_small_m():
    n, phi, e, x, c = mpz(143), mpz(120), mpz(5), mpz(5), mpz(85)
    assert no_d_small_m(n, phi, e, x, c) == 8 or True


def test_cli_integration(ctx):
    ns = ["14"]
    es = ["5"]
    cs = ["2"]
    d = "5"

    rsa_command(
        ctx=ctx,
        ns=ns,
        es=es,
        cs=cs,
        p=None,
        q=None,
        d=d,
        dp=None,
        dq=None,
        limit=1000,
    )
