from dataclasses import dataclass
from pathlib import Path
import argparse

from lktk.parser import lkml_parser


@dataclass
class Args:
    subcmd: str
    filepath: Path


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        prog="Looker Toolkit", description="unofficial looker CLI"
    )
    parser.add_argument("subcmd", type=Path)
    parser.add_argument("filepath", type=Path)
    args = parser.parse_args()

    return Args(
        subcmd=args.subcmd,
        filepath=args.filepath,
    )


def debug(args: Args) -> None:
    with open(args.filepath) as f:
        tree = lkml_parser.parse(f.read())
    print(tree.pretty())


def run() -> None:
    args = parse_args()

    match args.subcmd:
        case "debug":
            debug(args)
        case "fmt":
            pass
        case _:
            print(f"invalid subcmd: {args.subcmd}")
