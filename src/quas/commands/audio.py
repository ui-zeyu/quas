from pathlib import Path

import click

from quas.context import ContextObject


@click.group(help="Audio waveform analysis tools")
def app() -> None: ...


@click.command()
@click.pass_obj
@click.option("-t", "--tolerance", default=20, help="Frequency tolerance in Hz")
@click.option("-w", "--window", default=40, help="Window size in ms")
@click.option("-c", "--channel", type=int, help="Channel to use")
@click.option("--dtype", default="float64", help="Audio data type")
@click.argument("infile", type=Path)
def dtmf(
    ctx: ContextObject,
    infile: Path,
    tolerance: int,
    window: int,
    channel: int | None,
    dtype: str,
) -> None:
    from quas.audio.base import AudioSignal, select_channel
    from quas.audio.dtmf import DTMFRecognizer

    console = ctx["console"]
    sig = AudioSignal.read(infile, dtype=dtype)

    pipeline = select_channel(channel) | DTMFRecognizer(
        tolerance=tolerance, window_ms=window
    )
    digits = pipeline(sig)

    console.print(f"DTMF digits: {digits}")


@click.command()
@click.pass_obj
@click.option("-t", "--top", default=10, help="Top N frequencies")
@click.option("-c", "--channel", type=int, help="Channel to use")
@click.option("--dtype", default="float64", help="Audio data type")
@click.argument("infile", type=Path)
def frequency(
    ctx: ContextObject, infile: Path, top: int, channel: int | None, dtype: str
) -> None:
    import numpy as np

    from quas.audio.base import AudioSignal, select_channel
    from quas.audio.frequency import frequency_analyzer

    console = ctx["console"]
    sig = AudioSignal.read(infile, dtype=dtype)

    pipeline = select_channel(channel) | frequency_analyzer()
    freqs, magnitude = pipeline(sig)

    peak_indices = np.argsort(magnitude)[-top:]
    peak_freqs = np.sort(freqs[peak_indices]).astype(int)[::-1]
    peak_magnitudes = magnitude[peak_indices]

    console.print(f"Sample rate: {sig.sr} Hz")
    console.print(f"Top {top} frequencies:")
    for i, (freq, mag) in enumerate(zip(peak_freqs, peak_magnitudes, strict=True)):
        console.print(f"{i}. Frequency: {freq} Hz, Magnitude: {mag:.2e}")


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
    from quas.audio.base import AudioSignal, select_channel
    from quas.audio.lsb import lsb_extractor

    console = ctx["console"]
    sig = AudioSignal.read(infile, dtype=dtype)

    pipeline = select_channel(channel) | lsb_extractor(plane)
    results = list(pipeline(sig))

    with outfile.open("wb") as f:
        f.write(results[-1])

    console.print(f"Extracted LSB plane {plane} to {outfile}")


@click.command()
@click.pass_obj
@click.option("-t", "--tolerance", default=20, help="Frequency tolerance in Hz")
@click.option("-w", "--window", default=10, help="Window size in ms")
@click.option("-c", "--channel", type=int, help="Channel to use")
@click.option("--dtype", default="float64", help="Audio data type")
@click.argument("infile", type=Path)
def morse(
    ctx: ContextObject,
    infile: Path,
    tolerance: int,
    window: int,
    channel: int | None,
    dtype: str,
) -> None:
    from quas.audio.base import AudioSignal, select_channel
    from quas.audio.morse import MorseDecoder

    console = ctx["console"]
    sig = AudioSignal.read(infile, dtype=dtype)

    pipeline = select_channel(channel) | MorseDecoder(
        tolerance=tolerance, window_ms=window
    )
    morse_code, text = pipeline(sig)

    console.print(f"Morse: {morse_code}")
    console.print(f"Text:  {text}")


@click.command()
@click.pass_obj
@click.option("-t", "--title", default="Audio Analysis", help="Plot title")
@click.option("-w", "--window", default=20, help="Window size in ms")
@click.option("-c", "--channel", type=int, help="Channel to use")
@click.option("--dtype", default="float64", help="Audio data type")
@click.argument("infile", type=Path)
def visualize(
    ctx: ContextObject,
    infile: Path,
    title: str,
    window: int,
    channel: int | None,
    dtype: str,
) -> None:
    import matplotlib.pyplot as plt

    from quas.audio.base import AudioSignal, select_channel
    from quas.audio.visualize import AudioVisualizer

    sig = AudioSignal.read(infile, dtype=dtype)

    pipeline = select_channel(channel) | AudioVisualizer(title=title, window_ms=window)
    pipeline(sig)
    plt.show()


app.add_command(dtmf)
app.add_command(frequency)
app.add_command(lsb)
app.add_command(morse)
app.add_command(visualize)
