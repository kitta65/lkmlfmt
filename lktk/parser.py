from pathlib import Path

from lark import Lark, ParseTree

DIR = Path(__file__).parent

with open(DIR / "lkml.lark") as f:
    lkml_parser = Lark(f.read(), start="lkml")


def parse(path: Path) -> ParseTree:
    with open(path) as f:
        tree = lkml_parser.parse(f.read())

    return tree
