import binascii

from quas.crc.zip import crack

charset = b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "


def calculate_crc(data: bytes) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF


def test_crack_single():
    target_data = b"abcd"
    target_crc = calculate_crc(target_data)
    results = crack(4, {target_crc}, charset, jobs=1, crc2file={})

    assert target_crc in results.results
    assert target_data.decode() in results.results[target_crc]


def test_crack_multiple():
    target_data1 = b"ab"
    target_crc1 = calculate_crc(target_data1)
    target_data2 = b"cd"
    target_crc2 = calculate_crc(target_data2)
    targets = {target_crc1, target_crc2}

    results = crack(2, targets, charset, jobs=1, crc2file={})

    assert len(results.results) == 2
    for crc in [target_crc1, target_crc2]:
        assert crc in results.results
        assert len(results.results[crc]) >= 1
    assert target_data1.decode() in results.results[target_crc1]
    assert target_data2.decode() in results.results[target_crc2]


def test_crack_multiple_jobs():
    target_data = b"abc"
    target_crc = calculate_crc(target_data)
    results = crack(3, {target_crc}, charset, jobs=2, crc2file={})

    assert target_crc in results.results
    assert target_data.decode() in results.results[target_crc]


def test_crack_not_found():
    target_crc = 0xFFFFFFFF
    results = crack(4, {target_crc}, charset, jobs=1, crc2file={})

    assert len(results.results) == 0


def test_crack_special_chars():
    target_data = b"!@#"
    target_crc = calculate_crc(target_data)
    charset_special = b"!@#$"
    results = crack(3, {target_crc}, charset_special, jobs=1, crc2file={})

    assert target_crc in results.results
    assert target_data.decode() in results.results[target_crc]


def test_crack_numbers():
    target_data = b"1234"
    target_crc = calculate_crc(target_data)
    results = crack(4, {target_crc}, charset, jobs=1, crc2file={})

    assert target_crc in results.results
    assert len(results.results[target_crc]) >= 1
    assert target_data.decode() in results.results[target_crc]


def test_crack_unicode_decode_error():
    # Construct a byte sequence that cannot be decoded using utf-8
    # 0xFF is an invalid start byte in utf-8
    target_data = b"\xff\xff"
    target_crc = calculate_crc(target_data)
    charset_invalid = b"\xff"

    results = crack(2, {target_crc}, charset_invalid, jobs=1, crc2file={})

    # The result should be empty or not contain the target_crc
    # because the worker ignores UnicodeDecodeError
    assert (
        len(results.results) == 0
        or target_crc not in results.results
        or len(results.results[target_crc]) == 0
    )
