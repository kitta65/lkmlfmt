import pytest

from lktk.parser import lkml_parser
from lktk.formatter import LkmlFormatter


@pytest.mark.parametrize(
    "input_, output",
    [
        (
            """key1: value1 key2: value2""",
            """\
key1: value1
key2: value2""",
        ),
        (
            """key1: parent . child key2: value *""",
            """\
key1: parent.child
key2: value*""",
        ),
        # code block
        (
            """sql: code block ;;""",
            """sql: code block ;;""",
        ),
        (
            """\
sql: code
block ;;""",
            """\
sql:
  code
  block
;;""",
        ),
        # dict
        (
            """dict: {}""",
            """dict: {}""",
        ),
    ],
)
def test_formatter(input_: str, output: str) -> None:
    tree = lkml_parser.parse(input_)
    text = LkmlFormatter(tree, tree).print()
    assert text == output
