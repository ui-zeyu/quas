from pathlib import Path


def rev(infile: Path) -> bytes:
    return bytes(reversed(infile.read_bytes()))
