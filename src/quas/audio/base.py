from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np


@dataclass
class AudioSignal:
    y: np.ndarray
    sr: int

    @classmethod
    def read(cls, path: Path, dtype: str = "float64") -> AudioSignal:
        import soundfile as sf

        y, sr = sf.read(path, dtype=dtype)
        return cls(y, sr)


class Pipeline[I, O]:
    def __init__(self, step: Callable[[I], O]) -> None:
        self.step: Callable[[I], O] = step

    def __or__[T](self, next: Callable[[O], T]) -> Pipeline[I, T]:
        return Pipeline(lambda x: next(self.step(x)))

    def __call__(self, data: I) -> O:
        return self.step(data)


class Analyzer[T, U](Protocol):
    def __call__(self, data: T) -> U: ...


def select_channel(channel: int | None) -> Pipeline[AudioSignal, AudioSignal]:
    def analyze(sig: AudioSignal) -> AudioSignal:
        if channel is None or sig.y.ndim == 1:
            return sig
        return AudioSignal(sig.y[:, channel], sig.sr)

    return Pipeline(analyze)
