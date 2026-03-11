from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from quas.core import UseCase

if TYPE_CHECKING:
    from quas.audio.dtmf import DTMFPayload
    from quas.audio.frequency import FreqPayload
    from quas.audio.lsb import LsbPayload
    from quas.audio.morse import MorsePayload

app = typer.Typer(name="audio", help="Audio analysis tools", no_args_is_help=True)


@app.callback()
def callback() -> None: ...


@dataclass(kw_only=True)
class AudioUseCase[O](UseCase[O]):
    infile: Annotated[Path, typer.Argument(help="Input file")]
    channel: Annotated[
        int | None, typer.Option("--channel", "-c", help="Channel to use")
    ] = None
    dtype: Annotated[str, typer.Option("--dtype", help="Audio data type")] = "float64"


@dataclass(kw_only=True)
class DtmfUseCase(AudioUseCase["DTMFPayload"]):
    """Audio DTMF recognition."""

    GROUP = app
    COMMAND = "dtmf"

    tolerance: Annotated[
        int,
        typer.Option("--tolerance", "-t", help="Frequency tolerance in Hz"),
    ] = 20
    window: Annotated[
        int,
        typer.Option("--window", "-w", help="Window size in ms"),
    ] = 40

    def execute(self) -> DTMFPayload:
        from quas.audio.base import AudioSignal
        from quas.audio.dtmf import DTMFRecognizer

        sig = AudioSignal.read(self.infile, dtype=self.dtype)
        return DTMFRecognizer.perform(
            sig,
            tolerance=self.tolerance,
            window_ms=self.window,
            channel=self.channel,
        )


@dataclass(kw_only=True)
class FrequencyUseCase(AudioUseCase["FreqPayload"]):
    """Audio frequency analysis."""

    GROUP = app
    COMMAND = "frequency"

    top: Annotated[int, typer.Option("--top", "-t", help="Top N frequencies")] = 10

    def execute(self) -> FreqPayload:
        from quas.audio.base import AudioSignal, select_channel
        from quas.audio.frequency import frequency_analyzer

        sig = AudioSignal.read(self.infile, dtype=self.dtype)

        pipeline = select_channel(self.channel) | frequency_analyzer(top=self.top)
        return pipeline(sig)


@dataclass(kw_only=True)
class LsbUseCase(AudioUseCase["LsbPayload"]):
    """Audio LSB extraction."""

    GROUP = app
    COMMAND = "lsb"

    outfile: Annotated[Path, typer.Argument(help="Output file")]
    plane: Annotated[
        int,
        typer.Option("--plane", "-p", help="Bit plane to extract"),
    ] = 1
    dtype: Annotated[str, typer.Option("--dtype", help="Audio data type")] = "int16"

    def execute(self) -> LsbPayload:
        from quas.audio.base import AudioSignal, select_channel
        from quas.audio.lsb import lsb_extractor

        sig = AudioSignal.read(self.infile, dtype=self.dtype)

        pipeline = select_channel(self.channel) | lsb_extractor(
            plane=self.plane, outfile=self.outfile
        )
        return pipeline(sig)

    def effect(self, result: LsbPayload) -> None:
        result.save()
        self.ctx.obj["console"].print(result)


@dataclass(kw_only=True)
class MorseUseCase(AudioUseCase["MorsePayload"]):
    """Audio Morse code recognition."""

    GROUP = app
    COMMAND = "morse"

    tolerance: Annotated[
        int,
        typer.Option("--tolerance", "-t", help="Frequency tolerance in Hz"),
    ] = 20
    window: Annotated[
        int,
        typer.Option("--window", "-w", help="Window size in ms"),
    ] = 10

    def execute(self) -> MorsePayload:
        from quas.audio.base import AudioSignal
        from quas.audio.morse import MorseDecoder

        sig = AudioSignal.read(self.infile, dtype=self.dtype)
        return MorseDecoder.perform(
            sig,
            tolerance=self.tolerance,
            window_ms=self.window,
            channel=self.channel,
        )


@dataclass(kw_only=True)
class VisualizeUseCase(AudioUseCase[None]):
    """Audio visualization."""

    GROUP = app
    COMMAND = "visualize"

    title: Annotated[
        str,
        typer.Option("--title", "-t", help="Plot title"),
    ] = "Audio Analysis"
    window: Annotated[
        int,
        typer.Option("--window", "-w", help="Window size in ms"),
    ] = 20

    def execute(self) -> None:
        from quas.audio.base import AudioSignal, select_channel
        from quas.audio.visualize import AudioVisualizer

        sig = AudioSignal.read(self.infile, dtype=self.dtype)

        pipeline = select_channel(self.channel) | AudioVisualizer(
            title=self.title, window_ms=self.window
        )
        pipeline(sig)

    def effect(self, result: None) -> None:
        import matplotlib.pyplot as plt

        plt.show()
