import re

import pytest

from lktk.template import to_jinja


@pytest.mark.parametrize(
    "input_,output",
    [
        # no tag
        (
            "select 1",
            "select 1",
        ),
        # if
        (
            """\
select
{% if foo == 'bar' %} 1
{% else %} 2
{% endif %}""",
            """\
select
{% set lktk = 0 %}{% if True %}{% set lktk = 0 %} 1
{% set lktk = 1 %}{% else %}{% set lktk = 1 %} 2
{% set lktk = 2 %}{% endif %}{% set lktk = 2 %}""",
        ),
        # multiline
        (
            """\
select {%
  liquid
  assign x = "x"
  echo x
%}""",
            "select {% set lktk = 0 %}{% set x = 'x' %}{% set lktk = 0 %}",
        ),
        # comment
        (
            "select {% # comment %} 1",
            "select {% set lktk = 0 %}{% set x = 'x' %}{% set lktk = 0 %} 1",
        ),
        (
            """\
select {%
  # this
  # is
  # comment
%} 1""",
            "select {% set lktk = 0 %}{% set x = 'x' %}{% set lktk = 0 %} 1",
        ),
    ],
    ids=lambda x: re.sub(r"\s+", " ", x),
)
def test_to_jinja(input_: str, output: str) -> None:
    res, _ = to_jinja(input_)
    assert res == output
