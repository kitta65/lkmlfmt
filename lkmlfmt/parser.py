from pathlib import Path
from typing import Self

from lark import Lark, ParseTree, Token, Tree, Visitor

DIR = Path(__file__).parent
ParseTreeVisitor = Visitor[Token]

comments: list[Token] = []

lkml_parser = Lark(
    (DIR / "lkml.lark").read_text(),
    start="lkml",
    # https://lark-parser.readthedocs.io/en/latest/json_tutorial.html#step-2-lalr-1
    parser="lalr",
    lexer_callbacks={"COMMENT": comments.append},
)


class Position:
    line: int | None
    column: int | None
    end_line: int | None
    end_column: int | None

    def __init__(self) -> None:
        self.line = None
        self.column = None
        self.end_line = None
        self.end_column = None

    def extend(self, pos: Self | Token) -> None:
        if (
            pos.line is None
            or pos.column is None
            or pos.end_line is None
            or pos.end_column is None
        ):
            return

        if (
            self.line is None
            or self.column is None
            or self.end_line is None
            or self.end_column is None
        ):
            self.line = pos.line
            self.column = pos.column
            self.end_line = pos.end_line
            self.end_column = pos.end_column
            return

        if pos.line < self.line or (pos.line == self.line and pos.column < self.column):
            self.line = pos.line
            self.column = pos.column
        elif self.line < pos.line or (
            self.line == pos.line and self.column < pos.column
        ):
            self.end_line = pos.end_line
            self.end_column = pos.end_column


class PositionSetter(ParseTreeVisitor):
    def __default__(self, tree: ParseTree) -> None:
        pos = Position()
        for child in tree.children:
            if isinstance(child, Tree):
                pos.extend(child._position)  # type: ignore
            elif child is not None:  # Token is sometimes None...
                pos.extend(child)
        tree._position = pos  # type: ignore


# NOTE don't execute this function asynchronously
def parse(lkml: str, set_position: bool = False) -> tuple[ParseTree, list[Token]]:
    comments.clear()
    tree = lkml_parser.parse(lkml)

    if set_position:
        PositionSetter().visit(tree)
    return tree, comments
