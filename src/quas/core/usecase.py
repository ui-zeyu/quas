from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

import typer


@dataclass(kw_only=True)
class UseCase[O](ABC):
    GROUP: ClassVar[typer.Typer]
    COMMAND: ClassVar[str]

    ctx: typer.Context

    def __init_subclass__(cls, **kwargs: Any) -> None:
        import contextlib

        super().__init_subclass__(**kwargs)
        with contextlib.suppress(AttributeError):
            cls.GROUP.command(name=cls.COMMAND, help=cls.__doc__)(cls)

    @abstractmethod
    def execute(self) -> O: ...

    def effect(self, result: O) -> None:
        self.ctx.obj["console"].print(result)

    def __post_init__(self) -> None:
        result = self.execute()
        self.effect(result)
