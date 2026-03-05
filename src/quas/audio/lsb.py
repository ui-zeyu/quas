from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from rich.text import Text

from quas.audio.base import AudioSignal, Pipeline
from quas.core.protocols import CommandResult


@dataclass
class LsbPayload:
    plane: int
    outfile: Path
    results: list[bytes]


@dataclass
class LsbResult(CommandResult[LsbPayload]):
    data: LsbPayload

    def __rich__(self) -> Text:
        return Text(f"Extracted LSB plane {self.data.plane} to {self.data.outfile}")

    def save(self) -> None:
        with self.data.outfile.open("wb") as f:
            f.write(self.data.results[-1])


def lsb_extractor(plane: int, outfile: Path) -> Pipeline[AudioSignal, LsbResult]:
    def analyze(sig: AudioSignal) -> LsbResult:
        if not np.issubdtype(sig.y.dtype, np.integer):
            raise TypeError("LSB extraction requires integer samples")
        bits = (sig.y >> (plane - 1)) & 1

        def generate() -> Iterator[bytes]:
            yield from (col.tobytes() for col in np.packbits(bits, axis=0).T)
            yield np.packbits(bits.flatten()).tobytes()

        results = list(generate())
        return LsbResult(LsbPayload(plane=plane, outfile=outfile, results=results))

    return Pipeline(analyze)
