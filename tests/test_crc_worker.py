import string
from binascii import crc32

from quas.crc.zip import _worker, bruteforce


def test_worker_small_charset() -> None:
    charset = b"ab"
    targets = {crc32(b"ab") & 0xFFFFFFFF}

    results = _worker(b"", 2, targets, charset)

    assert len(results) > 0
    assert "ab" in results.get(targets.pop(), [])


def test_worker_prefix() -> None:
    charset = b"c"
    prefix = b"ab"
    targets = {crc32(b"abc") & 0xFFFFFFFF}

    results = _worker(prefix, 1, targets, charset)

    assert len(results) > 0
    assert "abc" in results.get(targets.pop(), [])


def test_worker_no_matches() -> None:
    charset = b"a"
    targets = {0xFFFFFFFF}

    results = _worker(b"", 1, targets, charset)

    assert len(results) == 0


def test_bruteforce_charset_ascii() -> None:
    targets = {crc32(b"abcd") & 0xFFFFFFFF}
    charset = string.ascii_letters[:10].encode()

    results = bruteforce(4, targets, charset, jobs=1, crc2file={})

    assert "abcd" in results.data.results[targets.pop()]


def test_bruteforce_multiple_targets() -> None:
    targets = {
        crc32(b"abc") & 0xFFFFFFFF,
        crc32(b"def") & 0xFFFFFFFF,
    }
    charset = b"abcdef"

    results = bruteforce(3, targets, charset, jobs=1, crc2file={})

    assert len(results.data.results) == 2
    assert any("abc" in v for v in results.data.results.values())
    assert any("def" in v for v in results.data.results.values())


def test_bruteforce_empty_charset() -> None:
    targets = {crc32(b"test") & 0xFFFFFFFF}
    charset = b""

    results = bruteforce(4, targets, charset, jobs=1, crc2file={})

    assert len(results.data.results) == 0


def test_bruteforce_case_sensitive() -> None:
    targets = {crc32(b"ABCD") & 0xFFFFFFFF}
    charset = b"abcd"

    results = bruteforce(4, targets, charset, jobs=1, crc2file={})

    assert len(results.data.results) == 0


def test_bruteforce_large_charset() -> None:
    targets = {crc32(b"!@#") & 0xFFFFFFFF}
    charset = b"!@#$%"

    results = bruteforce(3, targets, charset, jobs=1, crc2file={})

    assert "!@#" in results.data.results[targets.pop()]
