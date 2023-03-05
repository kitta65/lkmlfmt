from lark import ParseTree, Token

INDENT_WIDTH = 2


class LkmlFormatter:
    def __init__(self, tree: ParseTree, comments: ParseTree) -> None:
        self.tree = tree
        self.comments = comments
        self.curr_indent = 0

    def print(self) -> str:
        text = self.fmt()
        print(text)
        return text

    def fmt(
        self, tree: ParseTree | Token | list[ParseTree | Token] | None = None
    ) -> str:
        t = tree or self.tree

        if isinstance(t, list):
            elms = []
            for elm in t:
                elms.append(self.fmt(elm))
            return "\n".join(elms)

        if isinstance(t, Token):
            return t.value

        match t.data:
            case "lkml":
                return self.fmt_lkml(t)
            case "pair":
                return self.fmt_pair(t)
            case _:
                print(f"unknown data: {t.data}")
                return ""

    def fmt_lkml(self, lkml: ParseTree) -> str:
        return self.fmt(lkml.children)

    def fmt_pair(self, pair: ParseTree) -> str:
        key = self.fmt(pair.children[0])
        value = self.fmt(pair.children[1])
        return f"{key}: {value}"
