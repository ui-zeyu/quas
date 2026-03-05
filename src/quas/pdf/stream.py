import mmap
import re
from collections.abc import Iterator
from enum import Enum, auto
from pathlib import Path
from typing import Protocol, override

import click
import magic
import pikepdf
import pyparsing as pp
from rich.console import Console
from rich.panel import Panel

from quas.context import ContextObject
from quas.pdf.decoders import DecoderRegistry

MAX_CONTENT_LENGTH = 1000


class ScanStrategy(Enum):
    NORMAL = auto()
    REGEX = auto()

    def to_scanner(self) -> StreamScanner:
        match self:
            case ScanStrategy.NORMAL:
                return NormalScanner()
            case ScanStrategy.REGEX:
                return RegexScanner()


class StreamScanner(Protocol):
    def scan(self, infile: Path, console: Console) -> Iterator[tuple[str, bytes]]: ...


class NormalScanner(StreamScanner):
    @override
    def scan(self, infile: Path, console: Console) -> Iterator[tuple[str, bytes]]:
        with pikepdf.Pdf.open(infile) as doc:
            for obj in doc.objects:
                if not isinstance(obj, pikepdf.Stream):
                    continue

                data = obj.read_bytes()
                yield str(obj.objgen), data


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
    def scan(self, infile: Path, console: Console) -> Iterator[tuple[str, bytes]]:
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
                yield objgen.decode(), stream


@click.command(help="Extract and display all PDF streams")
@click.pass_obj
@click.argument("infile", type=Path)
@click.option(
    "-s",
    "--strategy",
    type=click.Choice(ScanStrategy, case_sensitive=False),
    default=ScanStrategy.NORMAL,
    help="Scanning strategy: normal or regex",
)
def stream(ctx: ContextObject, infile: Path, strategy: ScanStrategy) -> None:
    console = ctx["console"]

    scanner = strategy.to_scanner()
    for objgen, data in scanner.scan(infile, console):
        content = data.decode(errors="replace")
        content_type = magic.from_buffer(data)
        if len(content) > MAX_CONTENT_LENGTH:
            content = content[:MAX_CONTENT_LENGTH] + "..."

        panel = Panel(
            content,
            title=f"[bold cyan]Stream {objgen}[/bold cyan]",
            subtitle=f"[bold cyan]{content_type}[/bold cyan]",
            expand=True,
            highlight=True,
        )
        console.print(panel)
