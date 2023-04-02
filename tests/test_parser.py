import pytest

from lktk.parser import lkml_parser
from tests import utils


@pytest.mark.parametrize(
    "input_,output",
    [
        (
            "",
            """lkml
""",
        ),
        (
            'project_name: "my project name"',
            """lkml
    value_pair
        project_name
        "my project name"
""",
        ),
        (
            'key1: "value1" key2: "value2"',
            """lkml
    value_pair
        key1
        "value1"
    value_pair
        key2
        "value2"
""",
        ),
        (
            "# this is comment",
            """lkml
""",
        ),
        # ident
        (
            "yes_no: yes",
            """lkml
    value_pair
        yes_no
        yes
""",
        ),
        (
            '''20230101_is: "new year's day"''',
            """lkml
    value_pair
        20230101_is
        "new year's day"
""",
        ),
        (
            '_: "is valid identifier"',
            """lkml
    value_pair
        _
        "is valid identifier"
""",
        ),
        (  # space surrounding . is allowed
            "dot1: viewname.fieldname dot2: viewname . fieldname",
            """lkml
    value_pair
        dot1
        viewname.fieldname
    value_pair
        dot2
        viewname . fieldname
""",
        ),
        (  # space between +-* and ident is allowed
            "refine: + viewname exclude: -fieldname include: ALL_FIELDS *",
            """lkml
    value_pair
        refine
        + viewname
    value_pair
        exclude
        -fieldname
    value_pair
        include
        ALL_FIELDS *
""",
        ),
        # arr
        (
            "values: []",
            """lkml
    value_pair
        values
        arr\tNone
""",
        ),
        (
            'values: ["value1", "value2"]',
            """lkml
    value_pair
        values
        arr
            "value1"
            "value2"
""",
        ),
        (
            'values: ["value1", "value2",]',
            """lkml
    value_pair
        values
        arr
            "value1"
            "value2"
""",
        ),
        (
            'always_filter: [viewname.fieldname: "condition"]',
            """lkml
    value_pair
        always_filter
        arr
            value_pair
                viewname.fieldname
                "condition"
""",
        ),
        # dict
        (
            """dictionary: {}""",
            """lkml
    value_pair
        dictionary
        dict
""",
        ),
        (
            """dictionary: {key: "value"}""",
            """lkml
    value_pair
        dictionary
        dict
            value_pair
                key
                "value"
""",
        ),
        (
            """dictionary: {key1: "value1" key2: "value2"}""",
            """lkml
    value_pair
        dictionary
        dict
            value_pair
                key1
                "value1"
            value_pair
                key2
                "value2"
""",
        ),
        # named_dict
        (
            """named_dictionary: name {
  key: "value"
}""",
            """lkml
    value_pair
        named_dictionary
        named_dict
            name
            dict
                value_pair
                    key
                    "value"
""",
        ),
        # string
        (
            'key: "value # not comment"',
            """lkml
    value_pair
        key
        "value # not comment"
""",
        ),
        (
            r'key: "escaped\"string"',
            r"""lkml
    value_pair
        key
        "escaped\"string"
""",
        ),
        (
            '''key: "
multiline
string
"''',
            """lkml
    value_pair
        key
        "
multiline
string
"
""",
        ),
        # codeblock
        (
            "expression: #this is code block ;;",
            """lkml
    code_pair
        expression
        #this is code block
""",
        ),
        (
            """expression:
    multiline
    code block
;;""",
            """lkml
    code_pair
        expression
        multiline
    code block
""",  # strange indent but OK
        ),
        (
            "sql: code block 1;; sql_xxx: code block 2;;",
            """lkml
    code_pair
        sql
        code block 1
    code_pair
        sql_xxx
        code block 2
""",
        ),
        (
            "sql:;;",
            """lkml
    code_pair\tsql
""",
        ),
        # number
        (
            "num: 3.14",
            """lkml
    value_pair
        num
        3.14
""",
        ),
    ],
    ids=utils.shorten,
)
def test_parser(input_: str, output: str) -> None:
    tree = lkml_parser.parse(input_)
    assert tree.pretty(indent_str=" " * 4) == output
