from lktk.parser import lkml_parser

def test_dummy() -> None:
    tree = lkml_parser.parse('project_name: "my project name"')
    assert tree.pretty() == """lkml
  pair
    project_name
    "my project name"
"""
