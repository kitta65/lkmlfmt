import pytest

from lktk.parser import lkml_parser, comments
from lktk.formatter import LkmlFormatter


@pytest.mark.parametrize(
    "input_, output",
    [
        (
            """key1: value1 key2: 3.14""",
            """\
key1: value1
key2: 3.14""",
        ),
        # comment
        (
            """\
# comment 1
key1: value1
# comment 2.1
# comment 2.2
key2: value2""",
            """\
# comment 1
key1: value1
# comment 2.1
# comment 2.2
key2: value2""",
        ),
        (
            """\
# comment 
key: value""",  # noqa: W291
            """\
# comment
key: value""",
        ),
        # ident
        (
            """key1: parent . child key2: value *""",
            """\
key1: parent.child
key2: value*""",
        ),
        # arr
        (
            """values: []""",
            """values: []""",
        ),
        (
            """values: [ value ]""",
            """values: [ value ]""",
        ),
        (
            """values: [ value1, value2, [value3, value4], [value5] ]""",
            """values: [
  value1,
  value2,
  [
    value3,
    value4
  ],
  [ value5 ]
]""",
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
        (
            """dict: { key: value }""",
            """dict: {
  key: value
}""",
        ),
        (
            """dict: {
  key1: {key2: value2 key3: value3}
}""",
            """\
dict: {
  key1: {
    key2: value2
    key3: value3
  }
}""",
        ),
        # named dict
        (
            """dict: ident {
  key1: ident1 {}
  key2: ident2 { key3: ident3 { } }
}""",
            """\
dict: ident {
  key1: ident1 {}
  key2: ident2 {
    key3: ident3 {}
  }
}""",
        ),
    ],
)
def test_formatter(input_: str, output: str) -> None:
    tree = lkml_parser.parse(input_)
    text = LkmlFormatter(tree, comments).print()
    assert text == output
