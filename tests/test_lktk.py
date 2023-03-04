from lktk.parser import lkml_parser
import pytest


@pytest.mark.parametrize(
    "input_,output",
    [
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
    ],
)
def test_dummy(input_: str, output: str) -> None:
    tree = lkml_parser.parse(input_)
    assert tree.pretty() == output
