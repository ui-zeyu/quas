from collections.abc import Iterator

import numpy as np

from quas.audio.base import AudioSignal, Pipeline


def lsb_extractor(plane: int = 1) -> Pipeline[AudioSignal, Iterator[bytes]]:
    def analyze(sig: AudioSignal) -> Iterator[bytes]:
        if not np.issubdtype(sig.y.dtype, np.integer):
            raise TypeError("LSB extraction requires integer samples")
        bits = (sig.y >> (plane - 1)) & 1
        yield from (col.tobytes() for col in np.packbits(bits, axis=0).T)
        yield np.packbits(bits.flatten()).tobytes()

    return Pipeline(analyze)
