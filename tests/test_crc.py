from binascii import crc32

from quas.crc.zip import crack

charset = b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "


def test_crack_single():
    targets = {crc32(b"a") & 0xFFFFFFFF}
    results = crack(1, targets, charset, jobs=1, crc2file={})

    assert len(results.results) == 1
    assert "a" in results.results[targets.pop()]


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
    results = crack(3, targets, charset, jobs=1, crc2file={})

    assert len(results.results) == 0


def test_crack_special_chars():
    targets = {crc32(b"!@#") & 0xFFFFFFFF}
    results = crack(3, targets, charset, jobs=1, crc2file={})

    assert len(results.results) == 1
    assert "!@#" in results.results[targets.pop()]


def test_crack_numbers():
    targets = {crc32(b"1234") & 0xFFFFFFFF}
    results = crack(4, targets, charset, jobs=1, crc2file={})

    assert "1234" in results.results[targets.pop()]
