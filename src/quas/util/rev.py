import subprocess
from dataclasses import dataclass
from pathlib import Path

from rich.text import Text

from quas.core.protocols import CommandResult


@dataclass
class RevPayload:
    data: bytes
    outfile: Path


@dataclass
class RevResult(CommandResult[RevPayload]):
    data: RevPayload

    def __rich__(self) -> Text:
        if self.data.outfile == Path("-"):
            return Text("Reversed data displayed via hexyl.", style="green")
        return Text(f"Reversed data saved to {self.data.outfile}", style="green")

    def save_or_show(self) -> None:
        if self.data.outfile == Path("-"):
            subprocess.run(["hexyl"], input=self.data.data)
        else:
            self.data.outfile.write_bytes(self.data.data)


def perform_rev(infile: Path, outfile: Path) -> RevResult:
    data = bytes(reversed(infile.read_bytes()))
    return RevResult(RevPayload(data=data, outfile=outfile))
