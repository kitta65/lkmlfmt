from lktk.parser import lkml_parser
import pytest


@pytest.mark.parametrize(
    "input_,output",
    [
        (
            '',
            """lkml
""",
        ),
        # pair
        (
            'project_name: "my project name"',
            """lkml
    pair
        project_name
        "my project name"
""",
        ),
        (
            'key1: "value1" key2: "value2"',
            """lkml
    pair
        key1
        "value1"
    pair
        key2
        "value2"
""",
        ),
        # yesno
        (
            'yes_no: yes',
            """lkml
    pair
        yes_no
        yes
""",
        ),
        # arr
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
        # dict
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
        # named_dict
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
    assert tree.pretty(indent_str=" " * 4) == output
