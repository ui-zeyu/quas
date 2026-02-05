import pytest


def test_zip_integration():
    """Test ZIP CRC32 bruteforce"""
    from binascii import crc32

    from quas.crc.zip import bruteforce

    charset = "0123456789"
    targets = {crc32(b"0001") & 0xFFFFFFFF, crc32(b"0002") & 0xFFFFFFFF}

    results = bruteforce(4, targets, charset.encode(), jobs=1)

    assert len(results) == 2


def test_ihdr_integration():
    """Test PNG IHDR recovery with ihdr.png"""
    from pathlib import Path
    from struct import unpack

    png_file = Path(__file__).parent / "ihdr.png"
    data = png_file.read_bytes()

    from quas.crc.ihdr import IHDR_CHUNK_TYPE, PNG_SIGNATURE

    assert data[:8] == PNG_SIGNATURE
    chunk_length, chunk_type = unpack(">I4s", data[8:16])
    assert chunk_length == 0x0D
    assert chunk_type == IHDR_CHUNK_TYPE

    from PIL import Image, UnidentifiedImageError

    with pytest.raises(UnidentifiedImageError):
        Image.open(png_file)
