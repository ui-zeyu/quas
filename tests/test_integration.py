from binascii import crc32

from quas.crc.zip import crack

charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "


def test_zip_bruteforce_integration():
    targets = {crc32(b"test") & 0xFFFFFFFF, crc32(b"1234") & 0xFFFFFFFF}

    # size=4, 1 job
    results = crack(4, targets, charset.encode(), jobs=1, crc2file={})

    assert len(results.results) == 2
    for _crc, filenames in results.results.items():
        assert len(filenames) >= 1
        for filename in filenames:
            assert filename in ["test", "1234"]


def test_zip_bruteforce_multiprocess():
    targets = {crc32(b"abc") & 0xFFFFFFFF}

    # size=3, 4 jobs
    results = crack(3, targets, charset.encode(), jobs=4, crc2file={})

    assert len(results.results) == 1
    assert "abc" in results.results[targets.pop()]
