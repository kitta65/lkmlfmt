from contextlib import contextmanager
from typing import Generator
import re

from lark import ParseTree, Token

INDENT_WIDTH = 2
WS = re.compile(r"\s")


class LkmlFormatter:
    def __init__(self, tree: ParseTree, comments: list[Token]) -> None:
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
        t = self.tree if tree is None else tree

        if isinstance(t, list):
            elms = []
            for elm in t:
                elms.append(self.fmt(elm))
            return ("\n" if sep is None else sep).join(elms)

        if isinstance(t, Token):
            comments = self.fmt_leading_comments_of(t)
            return comments + WS.sub("", str(t.value))

        match t.data:
            case "arr":
                return self.fmt_arr(t)
            case "code_pair":
                return self.fmt_code_pair(t)
            case "dict":
                return self.fmt_dict(t)
            case "lkml":
                return self.fmt_lkml(t)
            case "named_dict":
                return self.fmt_named_dict(t)
            case "value_pair":
                return self.fmt_value_pair(t)
            case _:
                print(f"unknown data: {t.data}")
                return ""

    def fmt_arr(self, arr: ParseTree) -> str:
        if arr.children[0] is None:
            return "[]"

        values = self.fmt(arr.children, ",\n")

        lines = values.splitlines()
        if len(lines) == 1:
            return f"[ {values} ]"

        with self.indent():
            lines[:] = map(self.prepend_indent, lines)
            pairs = "\n".join(lines)
            return f"""[
{pairs}
]"""

    def fmt_code_pair(self, pair: ParseTree) -> str:
        # TODO fmt code block itself
        key = self.fmt(pair.children[0])
        value = str(pair.children[1])  # don't call self.fmt which remove WS
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

    def fmt_dict(self, dict_: ParseTree) -> str:
        pairs = self.fmt(dict_.children)
        if pairs == "":
            return "{}"

        lines = pairs.splitlines()
        with self.indent():
            lines[:] = map(self.prepend_indent, lines)
            pairs = "\n".join(lines)
            return f"""{{
{pairs}
}}"""

    def fmt_lkml(self, lookml: ParseTree) -> str:
        lkml = self.fmt(lookml.children)
        comments = ""
        while 0 < len(self.comments):
            comments += f"\n{str(self.comments.pop(0).value).strip()}"
        return (lkml + comments).strip()

    def fmt_named_dict(self, ndict: ParseTree) -> str:
        name = self.fmt(ndict.children[0])
        dict_ = self.fmt(ndict.children[1])
        # NOTE
        # do not have to take care of indentation of the children
        # cause this is a simple wrapper of fmt_dict
        return f"""{name} {dict_}"""

    def fmt_value_pair(self, pair: ParseTree) -> str:
        lcomments = self.fmt_leading_comments_of(pair.children[0])
        key = self.fmt(pair.children[0])
        value = self.fmt(pair.children[1])
        return f"{lcomments}{key}: {value}"

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

    def get_leading_comments(self, token: Token | ParseTree) -> list[Token]:
        if not isinstance(token, Token):
            return self.get_leading_comments(token.children[0])

        comments = []
        while (
            0 < len(self.comments)
            and token.line is not None
            and self.comments[0].line is not None
            and self.comments[0].line < token.line
        ):
            comments.append(self.comments.pop(0))
        return comments

    def fmt_leading_comments_of(self, token: Token | ParseTree) -> str:
        tokens = self.get_leading_comments(token)
        comments = ""
        if 0 < len(tokens):
            comments = "".join(map(lambda c: str(c.value).strip() + "\n", tokens))
        return comments
