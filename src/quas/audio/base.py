from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Self, cast, override, runtime_checkable

import numpy as np
import soundfile as sf


@dataclass(frozen=True, slots=True)
class AudioSignal:
    y: np.ndarray
    sr: int

    @classmethod
    def read(
        cls,
        path: Path,
        start: int = 0,
        stop: int | None = None,
        dtype="float64",
    ) -> Self:
        y, sr = cast(
            tuple[np.ndarray, int],
            sf.read(path, start, stop, dtype=dtype, always_2d=True),
        )
        return cls(y, sr)


@runtime_checkable
class Analyzer[I, O](Protocol):
    def __call__(self, data: I) -> O: ...


class Pipeline[I, O](Analyzer[I, O]):
    def __init__(self, step: Callable[[I], O]) -> None:
        self._step = step

    def __or__[T](self, next_step: Callable[[O], T]) -> Pipeline[I, T]:
        return Pipeline(lambda data: next_step(self._step(data)))

    @override
    def __call__(self, data: I) -> O:
        return self._step(data)


def select_channel(channel: int | None) -> Pipeline[AudioSignal, AudioSignal]:
    def analyze(sig: AudioSignal) -> AudioSignal:
        match channel, sig.y.ndim:
            case None, 1:
                y = sig.y
            case None, _:
                y = sig.y.mean(axis=1)
            case c, _:
                y = sig.y[:, c]
        return AudioSignal(y, sig.sr)

    return Pipeline(analyze)


def diff_channels() -> Pipeline[AudioSignal, np.ndarray]:
    return Pipeline(lambda sig: np.diff(sig.y, axis=1).T)
