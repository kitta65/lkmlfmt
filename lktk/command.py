import argparse
from dataclasses import dataclass
from pathlib import Path

from lktk.formatter import LkmlFormatter
from lktk.parser import parse


@dataclass
class Args:
    subcmd: str
    filepath: Path


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        prog="Looker Toolkit", description="unofficial looker CLI"
    )
    parser.add_argument("subcmd")
    parser.add_argument("filepath", type=Path)
    args = parser.parse_args()

    return Args(
        subcmd=args.subcmd,
        filepath=args.filepath,
    )


def run() -> None:
    args = parse_args()

    match args.subcmd:
        case "parse":
            tree, comments = parse(args.filepath.read_text())
            print(tree.pretty())
            print(comments)
        case "format" | "fmt":
            tree, comments = parse(args.filepath.read_text(), set_parent=True)
            formatter = LkmlFormatter(tree, comments)
            formatter.print()
        case _:
            print(f"invalid subcmd: {args.subcmd}")
