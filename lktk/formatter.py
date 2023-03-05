from contextlib import contextmanager
from typing import Generator
import re

from lark import ParseTree, Token

INDENT_WIDTH = 2
WS = re.compile(r"\s")


class LkmlFormatter:
    def __init__(self, tree: ParseTree, comments: ParseTree) -> None:
        self.tree = tree
        self.comments = comments  # TODO
        self.curr_indent = 0

    def print(self) -> str:
        text = self.fmt()
        print(text)
        return text

    # NOTE
    # parents take care of indentation of the children
    # parents take care of separator of the children
    def fmt(
        self,
        tree: ParseTree | Token | list[ParseTree | Token] | None = None,
        sep: str | None = None,
    ) -> str:
        t = tree or self.tree

        if isinstance(t, list):
            elms = []
            for elm in t:
                elms.append(self.fmt(elm))
            return ("\n" if sep is None else sep).join(elms)

        if isinstance(t, Token):
            return f"{t.value}"

        match t.data:
            case "lkml":
                return self.fmt_lkml(t)
            case "value_pair":
                return self.fmt_value_pair(t)
            case "code_pair":
                return self.fmt_code_pair(t)
            case _:
                print(f"unknown data: {t.data}")
                return ""

    def fmt_lkml(self, lkml: ParseTree) -> str:
        return self.fmt(lkml.children)

    def fmt_value_pair(self, pair: ParseTree) -> str:
        key = self.fmt(pair.children[0])
        value = WS.sub("", self.fmt(pair.children[1]))
        return f"{key}: {value}"

    def fmt_code_pair(self, pair: ParseTree) -> str:
        # TODO fmt code block itself
        key = self.fmt(pair.children[0])
        value = self.fmt(pair.children[1])
        lines = value.splitlines()
        if len(lines) == 1:
            return f"{key}: {value} ;;"

        with self.indent():
            # https://stackoverflow.com/questions/3000461/python-map-in-place
            lines[:] = map(self.prepend_indent, lines)
            value = "\n".join(lines)
            return f"""{key}:
{value}
;;"""

    def prepend_indent(self, line: str) -> str:
        return " " * INDENT_WIDTH * self.curr_indent + line

    # https://stackoverflow.com/questions/49733699/python-type-hints-and-context-managers
    @contextmanager
    def indent(self) -> Generator[None, None, None]:
        self.curr_indent += 1
        try:
            yield
        finally:
            self.curr_indent -= 1
