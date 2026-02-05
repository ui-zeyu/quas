from pathlib import Path
from struct import pack, unpack

from PIL import Image, UnidentifiedImageError

from quas.crc.ihdr import IHDR_CHUNK_TYPE, MAX_DIMENSION, PNG_SIGNATURE

DATA_DIR = Path(__file__).parent


def test_ihdr_png_exists() -> None:
    png_file = DATA_DIR / "ihdr.png"
    assert png_file.exists()
    assert png_file.stat().st_size > 0


def test_ihdr_png_signature() -> None:
    png_file = DATA_DIR / "ihdr.png"
    data = png_file.read_bytes()

    assert data[:8] == PNG_SIGNATURE


def test_ihdr_png_is_corrupted() -> None:
    png_file = DATA_DIR / "ihdr.png"

    try:
        Image.open(png_file)
        raise AssertionError("Should raise UnidentifiedImageError")
    except UnidentifiedImageError, OSError:
        pass


def test_ihdr_chunk_structure() -> None:
    png_file = DATA_DIR / "ihdr.png"
    data = png_file.read_bytes()

    chunk_length, chunk_type = unpack(">I4s", data[8:16])

    assert chunk_length == 0x0D
    assert chunk_type == IHDR_CHUNK_TYPE


def test_ihdr_bruteforce_dimensions() -> None:

    png_file = DATA_DIR / "ihdr.png"
    data = png_file.read_bytes()

    (width, height, ihdr_suffix, target) = unpack(">II5sI", data[16:33])

    assert width > 0
    assert height > 0
    assert target > 0


def test_ihdr_max_dimension_constant() -> None:
    assert MAX_DIMENSION == 5000


def test_ihdr_reconstruction() -> None:
    from binascii import crc32

    png_file = DATA_DIR / "ihdr.png"
    data = png_file.read_bytes()

    (width, height, ihdr_suffix, target) = unpack(">II5sI", data[16:33])

    ihdr = IHDR_CHUNK_TYPE + pack(">II5s", width, height, ihdr_suffix)
    crc = crc32(ihdr) & 0xFFFFFFFF

    assert crc != target


def test_ihdr_search_range() -> None:
    png_file = DATA_DIR / "ihdr.png"
    data = png_file.read_bytes()

    (width, height, _, _) = unpack(">II5sI", data[16:33])

    assert width <= MAX_DIMENSION
    assert height <= MAX_DIMENSION


def test_ihdr_png_minimum_size() -> None:
    png_file = DATA_DIR / "ihdr.png"
    data = png_file.read_bytes()

    assert len(data) >= 33
