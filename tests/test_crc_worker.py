from binascii import crc32

from quas.crc.zip import _worker, crack

charset = b"abcdefghijklmnopqrstuvwxyz"


def test_worker_success():
    targets = {crc32(b"ab") & 0xFFFFFFFF}

    results = _worker((b"", 2, targets, charset)).results
    assert crc32(b"ab") in results
    assert results[crc32(b"ab")] == ["ab"]


def test_worker_with_prefix():
    prefix = b"ab"
    targets = {crc32(b"abc") & 0xFFFFFFFF}

    results = _worker((prefix, 1, targets, charset)).results
    assert crc32(b"abc") in results
    assert results[crc32(b"abc")] == ["abc"]


def test_worker_not_found():
    targets = {0xFFFFFFFF}

    results = _worker((b"", 1, targets, charset)).results
    assert len(results) == 0


def test_crack_single():
    targets = {crc32(b"abcd") & 0xFFFFFFFF}
    results = crack(4, targets, charset, jobs=1, crc2file={})

    assert "abcd" in results.results[targets.pop()]


def test_crack_multiple():
    targets = {crc32(b"ab") & 0xFFFFFFFF, crc32(b"cd") & 0xFFFFFFFF}
    results = crack(2, targets, charset, jobs=1, crc2file={})

    assert len(results.results) == 2
    for _crc, filenames in results.results.items():
        assert len(filenames) >= 1
        for filename in filenames:
            assert filename in ["ab", "cd"]


def test_crack_multiple_jobs():
    targets = {crc32(b"abc") & 0xFFFFFFFF}
    results = crack(3, targets, charset, jobs=2, crc2file={})

    assert len(results.results) == 1
    assert "abc" in results.results[targets.pop()]


def test_crack_not_found():
    targets = {0xFFFFFFFF}
    results = crack(4, targets, charset, jobs=1, crc2file={})

    assert len(results.results) == 0


def test_crack_special_chars():
    targets = {crc32(b"!@#") & 0xFFFFFFFF}
    charset_special = b"!@#$"
    results = crack(3, targets, charset_special, jobs=1, crc2file={})

    assert len(results.results) == 1
    assert "!@#" in results.results[targets.pop()]
