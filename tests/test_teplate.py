import re

import pytest

from lktk.template import to_jinja, to_liquid
from tests import utils


@pytest.mark.parametrize(
    "liquid,jinja",
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
        # object
        (
            "select {{ '/* object */' }} 1",
            "select {% set lktk = 0 %}{{ obj }}{% set lktk = 0 %} 1",
        ),
    ],
    ids=lambda x: re.sub(r"\s+", " ", x),
)
def test_to_jinja(liquid: str, jinja: str) -> None:
    res, _ = to_jinja(liquid)
    assert res == jinja


@pytest.mark.parametrize(
    "jinja,liquid,tags",
    [
        # no tag
        (
            """\
select
{% set lktk = 0 %}{% if True %}{% set lktk = 0 %} 1
{% set lktk = 1 %}{% else %}{% set lktk = 1 %} 2
{% set lktk = 2 %}{% endif %}{% set lktk = 2 %}""",
            """\
select
{% if foo == 'bar' %} 1
{% else %} 2
{% endif %}""",
            ["{% if foo == 'bar' %}", "{% else %}", "{% endif %}"],
        ),
    ],
    ids=utils.shorten,
)
def test_to_liquid(jinja: str, liquid: str, tags: list[str]) -> None:
    res = to_liquid(jinja, tags)
    assert res == liquid
