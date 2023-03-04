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
    ],
)
def test_dummy(input_: str, output: str) -> None:
    tree = lkml_parser.parse(input_)
    assert tree.pretty() == output
