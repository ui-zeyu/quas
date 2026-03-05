import base64
import binascii
import re
import zlib
from collections.abc import Callable, Sequence
from typing import Protocol, override


class DecoderRegistry:
    DECODERS: dict[str, Callable[[bytes], bytes]] = {}

    @classmethod
    def registry(cls, decoder: type[Decoder]) -> None:
        for name in decoder.NAMES:
            cls.DECODERS[name] = decoder.decode

    @classmethod
    def decode(cls, data: bytes, filters: str | Sequence[str]) -> bytes:
        filters = (filters,) if isinstance(filters, str) else filters
        for filter in filters:
            try:
                data = cls.DECODERS[filter](data)
            except binascii.Error, zlib.error, KeyError, ValueError:
                break
        return data


class Decoder(Protocol):
    NAMES: Sequence[str]

    @classmethod
    def decode(cls, data: bytes) -> bytes: ...

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        DecoderRegistry.registry(cls)


class ZlibDecoder(Decoder):
    NAMES = ("/Fl", "/FlateDecode")

    @override
    @classmethod
    def decode(cls, data: bytes) -> bytes:
        return zlib.decompress(data)


class AsciiHexDecoder(Decoder):
    NAMES = ("/AHx", "/ASCIIHexDecode")

    @override
    @classmethod
    def decode(cls, data: bytes) -> bytes:
        data = re.sub(rb"[>\s]", b"", data)
        data = data if len(data) % 2 == 0 else data + b"0"
        return binascii.unhexlify(data)


class Ascii85Decoder(Decoder):
    NAMES = ("/A85", "/ASCII85Decode")

    @override
    @classmethod
    def decode(cls, data: bytes) -> bytes:
        data = re.sub(rb"[<~>\s]", b"", data)
        return base64.a85decode(data)
