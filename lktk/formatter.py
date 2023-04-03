import re
from contextlib import contextmanager
from typing import Generator

from lark import ParseTree, Token
from sqlfmt import api
from sqlfmt.line import Line

from lktk import parser, template
from lktk.exception import LktkException
from lktk.logger import logger

COMMENT_MARKER = "#LKTK_MARKER#"
COMMENT = re.compile(rf"{COMMENT_MARKER}")
BLANK_LINE = re.compile(r"^\s*$")
INDENT_WIDTH = 2
MODE = api.Mode()


class LkmlFormatter:
    def __init__(self, lkml: str) -> None:
        self.lkml = lkml
        self.curr_indent = 0

        tree, comments = parser.parse(lkml, set_position=True)
        self.tree = tree
        self.comments = comments

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
            return self.fmt_token(t)

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
                logger.warning(f"unknown data: {t.data}")
                return ""

    def fmt_arr(self, arr: ParseTree) -> str:
        if arr.children[0] is None:
            return "[]"

        values = self.fmt(arr.children, ",\n")

        lines = values.splitlines()
        if len(lines) == 1:
            return f"[ {values} ]"

        with self.indent():
            self.prepend_indent(lines)
            pairs = "\n".join(lines)
            return f"""[
{pairs},
]"""

    def fmt_code_pair(self, pair: ParseTree) -> str:
        lcomments = self.fmt_leading_comments_of(_token(pair.children[0]))
        key = self.fmt(pair.children[0])
        value = str(pair.children[1])

        if key == "html":
            value = _fmt_html(value)
            lines = value.splitlines()
            if len(lines) == 1:
                return f"{lcomments}{key}: {value} ;;"

            with self.indent():
                self.prepend_indent(lines)
                value = "\n".join(lines)
                return f"""{lcomments}{key}:
{value}
;;"""

        # sql_xxx: ... ;; or expression_xxx: ... ;;
        with self.indent():
            # https://docs.python.org/3/library/functions.html#property
            Line.prefix = property(  # type: ignore
                lambda s: " " * INDENT_WIDTH * (s.depth[0] + self.curr_indent)
            )
            value = _fmt_sql(value)

            if "\n" not in value:
                return f"{lcomments}{key}: {value.strip()} ;;"

            return f"""{lcomments}{key}:
{value}
;;"""

    def fmt_dict(self, dict_: ParseTree) -> str:
        pairs = self.fmt(dict_.children)
        if pairs == "":
            return "{}"

        lines = pairs.splitlines()
        with self.indent():
            self.prepend_indent(lines)
            pairs = "\n".join(lines)
            return f"""{{
{pairs}
}}"""

    def fmt_lkml(self, lookml: ParseTree) -> str:
        lkml = ""
        stmts = [child for child in lookml.children]
        for i, s in enumerate(stmts):
            if i == 0:
                lkml += self.fmt(s)
                continue

            prev_line: int | None = stmts[i - 1]._position.end_line  # type: ignore
            next_line: int | None = s._position.line  # type: ignore
            if prev_line is None or next_line is None:
                lkml += "\n"
                lkml += self.fmt(s)
                continue

            for _ in filter(
                lambda s: BLANK_LINE.match(s) is not None,
                self.lkml.splitlines()[prev_line:next_line],
            ):
                lkml += "\n"
            lkml += "\n"
            lkml += self.fmt(s)

        while 0 < len(self.comments):
            lkml += f"\n{str(self.comments.pop(0).value).rstrip()}"
        lkml = lkml.lstrip()  # in the case of lkml == "\n#comment"

        lines = []
        for line in lkml.splitlines():
            pieces = COMMENT.split(line)
            main = "".join(pieces[0::2])
            tcomments = " ".join(pieces[1::2])
            if tcomments == "":
                lines.append(f"{main}")
            else:
                lines.append(f"{main} {tcomments}")
        return "\n".join(lines)

    def fmt_named_dict(self, ndict: ParseTree) -> str:
        name = self.fmt(ndict.children[0])
        dict_ = self.fmt(ndict.children[1])
        # NOTE
        # do not have to take care of indentation of the children
        # cause this is a simple wrapper of fmt_dict
        return f"""{name} {dict_}"""

    def fmt_token(self, token: Token) -> str:
        lcomments = self.fmt_leading_comments_of(token)
        tcomments = self.fmt_trailing_comments_of(token)

        match token.type:
            case "STRING":
                t = str(token.value).strip()
            case _:
                t = str(token.value).replace(" ", "")

        return lcomments + t + tcomments

    def fmt_value_pair(self, pair: ParseTree) -> str:
        lcomments = self.fmt_leading_comments_of(_token(pair.children[0]))
        tcomments = self.fmt_trailing_comments_of(_token(pair.children[0]))

        key = self.fmt(pair.children[0])
        value = self.fmt(pair.children[1])
        return f"{lcomments}{key}:{tcomments} {value}"

    def prepend_indent(self, lines: list[str]) -> None:
        # https://stackoverflow.com/questions/3000461/python-map-in-place
        indent = " " * INDENT_WIDTH * self.curr_indent
        lines[:] = map(lambda line: (indent + line) if line != "" else "", lines)

    # https://stackoverflow.com/questions/49733699/python-type-hints-and-context-managers
    @contextmanager
    def indent(self) -> Generator[None, None, None]:
        self.curr_indent += 1
        try:
            yield
        finally:
            self.curr_indent -= 1

    def get_leading_comments(self, token: Token) -> list[Token]:
        comments = []
        while (
            0 < len(self.comments)
            and token.line is not None
            and self.comments[0].line is not None
            and self.comments[0].line < token.line
        ):
            comments.append(self.comments.pop(0))
        return comments

    # NOTE since looker doen't support inline comment, maybe len(result) == 1
    def get_trailing_comments(self, token: Token) -> list[Token]:
        comments = []
        idx = 0
        # line = self.comments[idx].line
        while (
            idx < len(self.comments)
            and token.line is not None
            and (line := self.comments[idx].line) is not None
            and line <= token.line
        ):
            if line == token.line:
                comments.append(self.comments.pop(idx))
                continue
            idx += 1  # if self.comments[idx] is leading comments
        return comments

    def fmt_leading_comments_of(self, token: Token) -> str:
        tokens = self.get_leading_comments(token)
        comments = ""
        if 0 < len(tokens):
            comments = "".join(map(lambda t: str(t.value).rstrip() + "\n", tokens))
        return comments

    def fmt_trailing_comments_of(self, token: Token) -> str:
        tokens = self.get_trailing_comments(token)
        if len(tokens) < 1:
            return ""
        comments = " ".join(map(lambda t: str(t.value).rstrip(), tokens))
        return COMMENT_MARKER + comments + COMMENT_MARKER


def _token(token: Token | ParseTree) -> Token:
    if isinstance(token, Token):
        return token
    raise LktkException()


# TODO
def _fmt_html(html: str) -> str:
    return html


# TODO format liquid tag and variales
def _fmt_sql(liquid: str) -> str:
    jinja, templates = template.to_jinja(liquid)
    # NOTE let's rely on sqlfmt for not only sql but also looker expression!
    jinja = api.format_string(jinja, mode=MODE).rstrip()
    liquid = template.to_liquid(jinja, templates)
    return liquid


def fmt(lkml: str) -> str:
    formatter = LkmlFormatter(lkml)
    return formatter.fmt()
