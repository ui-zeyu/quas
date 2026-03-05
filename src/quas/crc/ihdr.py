from binascii import crc32
from dataclasses import dataclass
from io import BytesIO
from struct import pack, unpack

from PIL import Image

PNG_SIGNATURE = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
IHDR_CHUNK_TYPE = b"IHDR"
MAX_DIMENSION = 5000


@dataclass
class IHDRRecoverResult:
    width: int
    height: int
    image: Image.Image


def recover_ihdr_dimensions(
    data: bytes,
    max_width: int,
    max_height: int,
) -> IHDRRecoverResult | None:
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("Invalid PNG signature")

    chunk_length, chunk_type = unpack(">I4s", data[8:16])
    if chunk_length != 0x0D or chunk_type != IHDR_CHUNK_TYPE:
        raise ValueError("First chunk is not IHDR")

    _, _, ihdr_suffix, target = unpack(">II5sI", data[16:33])

    for x in range(1, max_width + 1):
        for y in range(1, max_height + 1):
            ihdr_data = IHDR_CHUNK_TYPE + pack(">II5s", x, y, ihdr_suffix)
            crc = crc32(ihdr_data) & 0xFFFFFFFF
            if crc == target:
                chunk = b"\x00\x00\x00\x0d" + ihdr_data + pack(">I", crc)
                image_data = PNG_SIGNATURE + chunk + data[33:]

                try:
                    from PIL import UnidentifiedImageError

                    img = Image.open(BytesIO(image_data))
                    return IHDRRecoverResult(width=x, height=y, image=img)
                except UnidentifiedImageError:
                    continue
    return None
