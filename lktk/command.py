from dataclasses import dataclass
import argparse

from lktk.parser import lkml_parser


@dataclass
class Args:
    filepath: str


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        prog="Looker Toolkit", description="unofficial looker CLI"
    )
    parser.add_argument("filepath")
    args = parser.parse_args()

    return Args(filepath=args.filepath)


def run() -> None:
    args = parse_args()
    tree = lkml_parser.parse(args.filepath)
    tree.pretty()
