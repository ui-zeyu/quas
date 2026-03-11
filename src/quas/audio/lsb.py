from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from rich.text import Text

from quas.audio.base import AudioSignal, Pipeline


@dataclass
class LsbPayload:
    plane: int
    outfile: Path
    results: Sequence[bytes]

    def __rich__(self) -> Text:
        return Text(f"Extracted LSB plane {self.plane} to {self.outfile}")

    def save(self) -> None:
        with self.outfile.open("wb") as f:
            f.write(self.results[-1])


def lsb_extractor(plane: int, outfile: Path) -> Pipeline[AudioSignal, LsbPayload]:
    def analyze(sig: AudioSignal) -> LsbPayload:
        if not np.issubdtype(sig.y.dtype, np.integer):
            raise TypeError("LSB extraction requires integer samples")
        bits = (sig.y >> (plane - 1)) & 1

        def generate() -> Iterator[bytes]:
            yield from (col.tobytes() for col in np.packbits(bits, axis=0).T)
            yield np.packbits(bits.flatten()).tobytes()

        results = list(generate())
        return LsbPayload(plane=plane, outfile=outfile, results=results)

    return Pipeline(analyze)
