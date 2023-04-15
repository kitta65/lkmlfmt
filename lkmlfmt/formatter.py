import re
from contextlib import contextmanager
from typing import Any, Generator

from djhtml.lines import Line as DjHTMLLine  # type: ignore
from djhtml.modes import DjHTML  # type: ignore
from lark import ParseTree, Token
from sqlfmt import api
from sqlfmt.line import Line

from lkmlfmt import parser, template
from lkmlfmt.exception import LkmlfmtException
from lkmlfmt.logger import logger

COMMENT_MARKER = "#LKMLFMT_MARKER#"
COMMENT = re.compile(rf"{COMMENT_MARKER}")
BLANK_LINE = re.compile(r"^\s*$")
ESCAPED_STRING_SINGLE = re.compile(r'"(?P<inner>(.|\n)*?(?<!\\)(\\\\)*?)"')
ESCAPED_STRING_TRIPLE = re.compile(r'"""(?P<inner>(.|\n)*?(?<!\\)(\\\\)*?)"""')
NOT_AND_OR = re.compile(r"(?<!\w)(not|and|or)(?!\w)")
INDENT_WIDTH = 2


class LkmlFormatter:
    def __init__(self, lkml: str, clickhouse: bool) -> None:
        self.lkml = lkml
        self.curr_indent = 0

        tree, comments = parser.parse(lkml, set_position=True)
        self.tree = tree
        self.comments = comments
        self.mode = api.Mode(dialect_name="clickhouse" if clickhouse else "polyglot")

    # NOTE
    # parents take care of self.curr_indent, but children call fmt_indent()
    # parents take care of separator of the children
    def fmt(
        self,
        tree: ParseTree | Token | list[ParseTree | Token] | None = None,
        sep: str = "",
    ) -> str:
        t = self.tree if tree is None else tree

        if isinstance(t, list):
            return self.fmt_trees(t, sep)

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
                raise LkmlfmtException()

    def fmt_arr(self, arr: ParseTree) -> str:
        if arr.children[0] is None:
            return f"{self.fmt_indent()}[]"

        with self.indent():
            values = self.fmt(arr.children, ",")

        if "\n" not in values:
            return f"{self.fmt_indent()}[ {values.lstrip()} ]"

        return f"""{self.fmt_indent()}[
{values},
{self.fmt_indent()}]"""

    def fmt_code_pair(self, pair: ParseTree) -> str:
        lcomments = self.fmt_leading_comments_of(_token(pair.children[0]))
        key = self.fmt(pair.children[0]).lstrip()
        value = str(pair.children[1])

        if key.startswith("html"):
            with self.indent():
                indent = self.curr_indent
                f: Any = (
                    lambda s, w: " " * (w * (s.level + indent) + s.offset) + t
                    if (t := s.text.strip())
                    else t
                )
                # https://github.com/rtts/djhtml/blob/main/djhtml/lines.py
                DjHTMLLine.indent = f
                value = _fmt_html(value)

            if "\n" not in value:
                return f"{lcomments}{self.fmt_indent()}{key}: {value.lstrip()} ;;"

            return f"""{lcomments}{self.fmt_indent()}{key}:
{value}
{self.fmt_indent()};;"""

        # sql_xxx: ... ;; or expression_xxx: ... ;;
        with self.indent():
            # https://docs.python.org/3/library/functions.html#property
            Line.prefix = property(  # type: ignore
                lambda s: " " * INDENT_WIDTH * (s.depth[0] + self.curr_indent)
            )
            if key.startswith("sql"):
                value = self._fmt_sql(value)
            else:
                value = self._fmt_expr(value)

        if "\n" not in value:
            return f"{lcomments}{self.fmt_indent()}{key}: {value.lstrip()} ;;"

        if not value.startswith(" "):  # fallback if sqlfmt does not support
            value = " " * ((self.curr_indent + 1) * INDENT_WIDTH) + value

        return f"""{lcomments}{self.fmt_indent()}{key}:
{value}
{self.fmt_indent()};;"""

    def fmt_dict(self, dict_: ParseTree) -> str:
        with self.indent():
            pairs = self.fmt(dict_.children)

        if pairs == "":
            return f"{self.fmt_indent()}{{}}"

        return f"""{self.fmt_indent()}{{
{pairs}
{self.fmt_indent()}}}"""

    def fmt_lkml(self, lookml: ParseTree) -> str:
        stmts = [child for child in lookml.children]
        lkml = self.fmt(stmts)

        while 0 < len(self.comments):
            # comments may have trailing space
            lkml += f"\n{str(self.comments.pop(0).value).rstrip()}"
        lkml = lkml.lstrip()  # in the case of lkml == "\n#comment"

        # handle trailing comments
        lines = []
        for line in lkml.splitlines():
            pieces = COMMENT.split(line)
            main = "".join(pieces[0::2])
            tcomments = " ".join(pieces[1::2])
            if tcomments == "":
                lines.append(f"{main}")
            else:
                lines.append(f"{main} {tcomments}")

        return "\n".join(lines) + "\n"

    def fmt_named_dict(self, ndict: ParseTree) -> str:
        name = self.fmt(ndict.children[0]).lstrip()
        dict_ = self.fmt(ndict.children[1]).lstrip()
        # NOTE
        # since this is a simple wrapper of fmt_dict
        # do not have to increment curr_indent
        return f"""{self.fmt_indent()}{name} {dict_}"""

    def fmt_token(self, token: Token) -> str:
        lcomments = self.fmt_leading_comments_of(token)
        tcomments = self.fmt_trailing_comments_of(token)

        match token.type:
            case "STRING":
                t = str(token.value).strip()
            case _:
                t = str(token.value).replace(" ", "")

        return lcomments + self.fmt_indent() + t + tcomments

    def fmt_value_pair(self, pair: ParseTree) -> str:
        lcomments = self.fmt_leading_comments_of(_token(pair.children[0]))
        tcomments = self.fmt_trailing_comments_of(_token(pair.children[0]))

        key = self.fmt(pair.children[0]).lstrip()
        value = self.fmt(pair.children[1]).lstrip()

        return f"{lcomments}{self.fmt_indent()}{key}:{tcomments} {value}"

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

    def fmt_indent(self) -> str:
        return " " * INDENT_WIDTH * self.curr_indent

    def fmt_leading_comments_of(self, token: Token) -> str:
        tokens = self.get_leading_comments(token)
        comments = ""
        if 0 < len(tokens):
            comments = "".join(
                map(lambda t: self.fmt_indent() + str(t.value).rstrip() + "\n", tokens)
            )
        return comments

    def fmt_trailing_comments_of(self, token: Token) -> str:
        tokens = self.get_trailing_comments(token)
        if len(tokens) < 1:
            return ""
        comments = " ".join(map(lambda t: str(t.value).rstrip(), tokens))
        return COMMENT_MARKER + comments + COMMENT_MARKER

    def fmt_trees(self, trees: list[Token | ParseTree], sep: str = "") -> str:
        joined = ""

        for i, t in enumerate(trees):
            if i == 0:
                joined += self.fmt(t)
                continue

            prev_line: int | None = None
            next_line: int | None = None
            if isinstance(t, Token):
                next_line = t.line
            else:
                next_line: int | None = t._position.line  # type: ignore

            prev = trees[i - 1]
            if isinstance(prev, Token):
                prev_line = prev.end_line
            else:
                prev_line = prev._position.end_line  # type: ignore

            joined += sep
            if prev_line is None or next_line is None:
                joined += f"\n{self.fmt(t)}"
                continue

            for _ in filter(
                lambda s: BLANK_LINE.match(s) is not None,
                self.lkml.splitlines()[prev_line:next_line],
            ):
                joined += "\n"

            joined += "\n"
            joined += self.fmt(t)

        return joined

    def _fmt_sql(self, liquid: str) -> str:
        jinja, templates, dummies = template.to_jinja(liquid, "sqlfmt")
        jinja = api.format_string(jinja, mode=self.mode).rstrip()
        liquid = template.to_liquid_sqlfmt(jinja, templates, dummies)
        return liquid

    # NOTE let's rely on sqlfmt for not only sql but also looker expression!
    def _fmt_expr(self, liquid: str) -> str:
        # convert looker expr into sql
        temp = liquid
        temp = temp.replace("case", "lkmlfmt_case")
        temp = temp.replace("when", "lkmlfmt_when")
        temp = ESCAPED_STRING_SINGLE.sub(r'"""\g<inner>"""', temp)  # " -> """

        temp = self._fmt_sql(temp)

        # convert sql into looker expression
        temp = ESCAPED_STRING_TRIPLE.sub(r'"\g<inner>"', temp)
        temp = temp.replace("lkmlfmt_when", "when")
        temp = temp.replace("lkmlfmt_case", "case")

        splited = ESCAPED_STRING_SINGLE.split(temp)
        expr = ""
        for i, s in enumerate(splited):
            match divmod(i, 4)[1]:  # mod
                case 0:
                    uppered = NOT_AND_OR.sub(lambda x: x.group(0).upper(), s)
                    expr += uppered
                case 1:
                    expr += f'"{s}"'

        return expr


def _token(token: Token | ParseTree) -> Token:
    if isinstance(token, Token):
        return token
    raise LkmlfmtException()


def _fmt_html(liquid: str) -> str:
    jinja, templates, dummies = template.to_jinja(liquid, "djhtml")
    jinja = DjHTML(jinja).indent(2)
    liquid = template.to_liquid_djhtml(jinja, templates, dummies)
    return liquid


def fmt(lkml: str, clickhouse: bool) -> str:
    formatter = LkmlFormatter(lkml, clickhouse)
    return formatter.fmt()
