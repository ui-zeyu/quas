from collections.abc import Iterator
from pathlib import Path

import click
import numpy as np

from quas.audio.base import AudioSignal, Pipeline, select_channel
from quas.context import ContextObject


def lsb_extractor(plane: int = 1) -> Pipeline[AudioSignal, Iterator[bytes]]:
    def analyze(sig: AudioSignal) -> Iterator[bytes]:
        if not np.issubdtype(sig.y.dtype, np.integer):
            raise TypeError("LSB extraction requires integer samples")
        bits = (sig.y >> (plane - 1)) & 1
        yield from (col.tobytes() for col in np.packbits(bits, axis=0).T)
        yield np.packbits(bits.flatten()).tobytes()

    return Pipeline(analyze)


@click.command()
@click.pass_obj
@click.option("-p", "--plane", default=1, help="Bit plane to extract")
@click.option("-c", "--channel", type=int, help="Channel to use")
@click.option("--dtype", default="int16", help="Audio data type")
@click.argument("infile", type=Path)
@click.argument("outfile", type=Path)
def lsb(
    ctx: ContextObject,
    infile: Path,
    outfile: Path,
    plane: int,
    channel: int | None,
    dtype: str,
) -> None:
    console = ctx["console"]
    sig = AudioSignal.read(infile, dtype=dtype)

    pipeline = select_channel(channel) | lsb_extractor(plane)
    results = list(pipeline(sig))

    with outfile.open("wb") as f:
        f.write(results[-1])

    console.print(f"Extracted LSB plane {plane} to {outfile}")
