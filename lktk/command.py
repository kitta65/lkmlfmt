from dataclasses import dataclass
from pathlib import Path
import argparse

from lktk.parser import parse
from lktk.formatter import LkmlFormatter


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
            parse(args.filepath)
        case "fmt":
            tree = parse(args.filepath)
            formatter = LkmlFormatter(tree, tree)
            formatter.print()
        case _:
            print(f"invalid subcmd: {args.subcmd}")
