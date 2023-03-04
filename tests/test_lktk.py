from lktk.parser import lkml_parser
import pytest


@pytest.mark.parametrize(
    "input_,output",
    [
        (
            '',
            """lkml\tNone
""",
        ),
        (
            'project_name: "my project name"',
            """lkml
  pair
    project_name
    "my project name"
""",
        ),
        (
            'yes_no: yes',
            """lkml
  pair
    yes_no
    yes
""",
        ),
        (
            'values: []',
            """lkml
  pair
    values
    arr\tNone
""",
        ),
        (
            'values: ["value1", "value2"]',
            """lkml
  pair
    values
    arr
      "value1"
      "value2"
""",
        ),
        (
            '''dictionary: {}''',
            """lkml
  pair
    dictionary
    dict\tNone
""",
        ),
        (
            '''dictionary: {
  key: "value"
}''',
            """lkml
  pair
    dictionary
    dict
      pair
        key
        "value"
""",
        ),
        (
            '''named_dictionary: name {
  key: "value"
}''',
            """lkml
  pair
    named_dictionary
    named_dict
      name
      dict
        pair
          key
          "value"
""",
        ),
    ],
)
def test_dummy(input_: str, output: str) -> None:
    tree = lkml_parser.parse(input_)
    assert tree.pretty() == output
