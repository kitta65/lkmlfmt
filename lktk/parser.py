from pathlib import Path

from lark import Lark

DIR = Path(__file__).parent

with open(DIR / "lkml.lark") as f:
    lkml_parser = Lark(f.read(), start="lkml")
