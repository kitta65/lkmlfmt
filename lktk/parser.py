import weakref
from pathlib import Path

from lark import Lark, ParseTree, Token, Tree, Visitor

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


# TODO remove if not needed
# https://lark-parser.readthedocs.io/en/latest/recipes.html#keeping-track-of-parents-when-visiting
class ParentSetter(Visitor[Token]):  # Visitor[Token] means Visitor of ParseTree
    def __default__(self, tree: ParseTree) -> None:
        for child in tree.children:
            if isinstance(child, Tree):
                child._parent = weakref.ref(tree)  # type: ignore


# NOTE don't execute this function asynchronously
def parse(lkml: str, set_parent: bool = False) -> tuple[ParseTree, list[Token]]:
    comments.clear()
    tree = lkml_parser.parse(lkml)
    if set_parent:
        ParentSetter().visit(tree)
    return tree, comments
