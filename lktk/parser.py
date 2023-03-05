from pathlib import Path

from lark import Lark, ParseTree, Token

DIR = Path(__file__).parent


comments: list[Token] = []

with open(DIR / "lkml.lark") as f:
    lkml_parser = Lark(
        f.read(),
        start="lkml",
        # https://lark-parser.readthedocs.io/en/latest/json_tutorial.html#step-2-lalr-1
        parser="lalr",
        lexer_callbacks={"COMMENT": comments.append},
    )


# NOTE don't execute this function asynchronously
def parse(path: Path) -> tuple[ParseTree, list[Token]]:
    comments.clear()
    with open(path) as f:
        tree = lkml_parser.parse(f.read())
    return tree, comments
