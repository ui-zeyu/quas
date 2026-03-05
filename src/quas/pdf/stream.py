import mmap
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Protocol, override

import magic
import pikepdf
import pyparsing as pp
from rich.console import Console, Group
from rich.panel import Panel

from quas.core.protocols import CommandResult
from quas.pdf.decoders import DecoderRegistry

MAX_CONTENT_LENGTH = 1000


@dataclass
class StreamItem:
    objgen: str
    data: bytes


@dataclass
class StreamPayload:
    items: Sequence[StreamItem]


@dataclass
class StreamResult(CommandResult[StreamPayload]):
    data: StreamPayload

    def __rich__(self) -> Group:
        panels = []
        for item in self.data.items:
            content = item.data.decode(errors="replace")
            content_type = magic.from_buffer(item.data)
            if len(content) > MAX_CONTENT_LENGTH:
                content = content[:MAX_CONTENT_LENGTH] + "..."

            panels.append(
                Panel(
                    content,
                    title=f"[bold cyan]Stream {item.objgen}[/bold cyan]",
                    subtitle=f"[bold cyan]{content_type}[/bold cyan]",
                    expand=True,
                    highlight=True,
                )
            )
        return Group(*panels)


class ScanStrategy(Enum):
    NORMAL = auto()
    REGEX = auto()

    def to_scanner(self) -> StreamScanner:
        match self:
            case ScanStrategy.NORMAL:
                return NormalScanner()
            case ScanStrategy.REGEX:
                return RegexScanner()

    @classmethod
    def perform_scan(
        cls,
        infile: Path,
        strategy: ScanStrategy,
        console: Console,
    ) -> StreamResult:
        scanner = strategy.to_scanner()
        items = list(scanner.scan(infile, console))
        return StreamResult(StreamPayload(items))


class StreamScanner(Protocol):
    def scan(self, infile: Path, console: Console) -> Iterator[StreamItem]: ...


class NormalScanner(StreamScanner):
    @override
    def scan(self, infile: Path, console: Console) -> Iterator[StreamItem]:
        with pikepdf.Pdf.open(infile) as doc:
            for obj in doc.objects:
                if not isinstance(obj, pikepdf.Stream):
                    continue

                data = obj.read_bytes()
                yield StreamItem(str(obj.objgen), data)


class RegexScanner(StreamScanner):
    @staticmethod
    def dict_parser() -> pp.ParserElement:
        LBRACK, RBRACK = map(pp.Suppress, "[]")
        LDICT, RDICT = map(pp.Suppress, ["<<", ">>"])

        dict_key = pp.Combine("/" + pp.Word(re.sub(r"/\[\]<>", "", pp.printables)))
        dict_value = pp.Forward()

        dict_number = pp.common.number
        dict_bool = pp.Keyword("true") | pp.Keyword("false")
        dict_null = pp.Keyword("null")
        dict_string = pp.nested_expr("(", ")") | pp.nested_expr("<", ">")
        dict_reference = pp.Group(pp.Word(pp.nums) + pp.Word(pp.nums) + pp.Keyword("R"))
        dict_array = pp.Group(LBRACK + pp.ZeroOrMore(dict_value) + RBRACK)
        dict_entry = pp.Group(dict_key + dict_value)
        pdf_dict = pp.Dict(LDICT + pp.ZeroOrMore(dict_entry) + RDICT)

        dict_value <<= (
            dict_key
            | dict_reference
            | dict_number
            | dict_bool
            | dict_null
            | dict_string
            | dict_array
            | pdf_dict
        )

        return pdf_dict

    OBJ_PATTERN: re.Pattern = re.compile(
        rb"(\d+\s+\d+)\s+obj\s*(<<.*?>>)\s*(stream|endobj)\b",
        re.DOTALL,
    )
    DICT_PARSER: pp.ParserElement = dict_parser()

    @override
    def scan(self, infile: Path, console: Console) -> Iterator[StreamItem]:
        with (
            open(infile, "rb") as f,
            mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm,
        ):
            for match in self.OBJ_PATTERN.finditer(mm):
                objgen, chunk, terminator = match.groups()
                if terminator == b"endobj":
                    continue

                chunk = chunk.decode("latin-1")
                try:
                    ast = self.DICT_PARSER.parse_string(chunk)
                except pp.ParseException as e:
                    console.log(chunk, e)
                    continue

                begin = match.end()
                while mm[begin : begin + 1].isspace():
                    begin += 1

                try:
                    length = int(ast.get("/Length"))
                    stream = mm[begin : begin + length]
                except ValueError:
                    if (end := mm.find(b"endstream", begin)) != -1:
                        stream = mm[begin:end]
                    else:
                        continue

                if filters := ast.get("/Filter"):
                    stream = DecoderRegistry.decode(stream, filters)
                yield StreamItem(objgen.decode(), stream)
