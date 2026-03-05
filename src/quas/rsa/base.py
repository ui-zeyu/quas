from dataclasses import dataclass

from rich.panel import Panel

from quas.core.protocols import CommandResult


@dataclass
class RSAPayload:
    m: int
    plaintext: str
    status: str


@dataclass
class RSAResult(CommandResult[RSAPayload]):
    data: RSAPayload

    def __rich__(self) -> Panel:
        return Panel(
            f"[bold]m:[/bold] {self.data.m}\n[bold]plaintext:[/bold] {self.data.plaintext}",
            title=self.data.status,
            border_style="green",
        )
