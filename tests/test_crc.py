from binascii import crc32
from pathlib import Path

from quas.crc.ihdr import PNG_SIGNATURE
from quas.crc.zip import bruteforce

DATA_DIR = Path(__file__).parent


def test_bruteforce_size_4() -> None:
    from binascii import crc32

    targets = {crc32(b"0001") & 0xFFFFFFFF, crc32(b"0002") & 0xFFFFFFFF}
    charset = b"0123456789"

    results = bruteforce(4, targets, charset, jobs=1)

    assert len(results) == 2
    for _crc, filenames in results.items():
        assert len(filenames) >= 1
        for filename in filenames:
            assert len(filename) == 4


def test_bruteforce_small_size() -> None:
    targets = {crc32(b"abc") & 0xFFFFFFFF}
    charset = b"abc"

    results = bruteforce(3, targets, charset, jobs=1)

    assert len(results) == 1
    assert "abc" in results[targets.pop()]


def test_bruteforce_no_match() -> None:
    targets = {0xFFFFFFFF}
    charset = b"abc"

    results = bruteforce(3, targets, charset, jobs=1)

    assert len(results) == 0


def test_zip_signature() -> None:
    assert PNG_SIGNATURE == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"


def test_bruteforce_charset_all_printable() -> None:
    import string

    targets = {crc32(b"1234") & 0xFFFFFFFF}
    charset = string.printable.strip()[:10].encode()

    results = bruteforce(4, targets, charset, jobs=1)

    assert "1234" in results[targets.pop()]
