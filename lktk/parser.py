from pathlib import Path

from lark import Lark, ParseTree, Token, Visitor

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


# https://lark-parser.readthedocs.io/en/latest/recipes.html#keeping-track-of-parents-when-visiting
class ParentSetter(Visitor[Token]):  # Visitor[Token] means Visitor of ParseTree
    def __default__(self, tree: ParseTree) -> None:
        for child in tree.children:
            if isinstance(child, Token):
                continue
            child._parent = tree  # type: ignore


# NOTE don't execute this function asynchronously
def parse(path: Path, set_parent: bool = False) -> tuple[ParseTree, list[Token]]:
    comments.clear()
    with open(path) as f:
        tree = lkml_parser.parse(f.read())
    if set_parent:
        ParentSetter().visit(tree)
    return tree, comments
