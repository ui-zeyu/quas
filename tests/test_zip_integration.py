import zipfile
from pathlib import Path

from quas.crc import bruteforce

DATA_DIR = Path(__file__).parent


def test_zip_4crc_file_size() -> None:
    zip_file = DATA_DIR / "4crc.zip"
    assert zip_file.exists()

    with zipfile.ZipFile(zip_file, "r") as zf:
        files_size_4 = [f for f in zf.infolist() if f.file_size == 4]

        assert len(files_size_4) == 6

        crcs = {f.CRC for f in files_size_4}
        expected_crcs = {
            0xCE70D424,
            0xC3F17511,
            0xF90C8A70,
            0x35EB81EE,
            0xA695678A,
            0x9244E5AF,
        }
        assert crcs == expected_crcs


def test_zip_4crc_bruteforce() -> None:
    from binascii import crc32

    targets = {crc32(b"0001") & 0xFFFFFFFF, crc32(b"0002") & 0xFFFFFFFF}
    charset = b"0123456789"

    results = bruteforce(4, targets, charset)

    assert len(results) == 2
    for _crc, filenames in results.items():
        assert len(filenames) >= 1
        for fname in filenames:
            assert len(fname) == 4


def test_zip_4crc_specific_crc() -> None:
    from binascii import crc32

    charset = b"0123456789"
    target_crc = crc32(b"1234") & 0xFFFFFFFF

    results = bruteforce(4, {target_crc}, charset)

    assert target_crc in results
    assert len(results[target_crc]) >= 1
    assert "1234" in results[target_crc]


def test_zip_flag_file_exists() -> None:
    zip_file = DATA_DIR / "4crc.zip"

    with zipfile.ZipFile(zip_file, "r") as zf:
        flag_files = [f for f in zf.infolist() if "flag" in f.filename.lower()]

        assert len(flag_files) == 1
        assert flag_files[0].file_size == 403
        assert flag_files[0].CRC == 0x36595A8F


def test_zip_file_count() -> None:
    zip_file = DATA_DIR / "4crc.zip"

    with zipfile.ZipFile(zip_file, "r") as zf:
        assert len(zf.infolist()) == 7
