from dataclasses import dataclass
from pathlib import Path
import argparse

from lktk.parser import lkml_parser


@dataclass
class Args:
    filepath: Path


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        prog="Looker Toolkit", description="unofficial looker CLI"
    )
    parser.add_argument("filepath", type=Path)
    args = parser.parse_args()

    return Args(filepath=args.filepath)


def run() -> None:
    args = parse_args()
    with open(args.filepath) as f:
        tree = lkml_parser.parse(f.read())
    tree.pretty()
