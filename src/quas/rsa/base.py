from dataclasses import dataclass

from rich.console import Group
from rich.panel import Panel


@dataclass
class RSAPayload:
    m: int
    plaintext: str
    status: str

    def __rich__(self) -> Group:
        return Group(
            Panel(
                f"[bold green]Decryption Successful![/bold green]\n"
                f"[cyan]Integer:[/cyan] {self.m}\n"
                f"[cyan]Plaintext:[/cyan] {self.plaintext}",
                title=f"RSA - {self.status}",
            )
        )
