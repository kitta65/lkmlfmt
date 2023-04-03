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
{% set LKTK_MARKER = 0 %}{% if True %}{% set LKTK_MARKER = 0 %} 1
{% set LKTK_MARKER = 1 %}{% else %}{% set LKTK_MARKER = 1 %} 2
{% set LKTK_MARKER = 2 %}{% endif %}{% set LKTK_MARKER = 2 %}""",
        ),
        # raw
        (
            """\
select {% raw %}
"{{string literal}}"
{% endraw %}
""",
            """\
select {% set LKTK_MARKER = 0 %}{% raw %}{% set LKTK_MARKER = 0 %}
"{{string literal}}"
{% set LKTK_MARKER = 1 %}{% endraw %}{% set LKTK_MARKER = 1 %}
""",
        ),
        # multiline
        (
            """\
select {%
  liquid
  assign x = "x"
  echo x
%}""",
            """\
select {% set LKTK_MARKER = 0 %}{% set x = 'x' %}{% set LKTK_MARKER = 0 %}""",
        ),
        # comment
        (
            "select {% # comment %} 1",
            """\
select {% set LKTK_MARKER = 0 %}{% set x = 'x' %}{% set LKTK_MARKER = 0 %} 1""",
        ),
        (
            """\
select {%
  # this
  # is
  # comment
%} 1""",
            """\
select {% set LKTK_MARKER = 0 %}{% set x = 'x' %}{% set LKTK_MARKER = 0 %} 1""",
        ),
        # {{...}}
        (
            "select {{ '1' }}",
            "select {% set LKTK_MARKER = 0 %}{{ var }}{% set LKTK_MARKER = 0 %}",
        ),
        # ${...}
        (
            "select ${x}",
            "select {% set LKTK_MARKER = 0 %}{{ var }}{% set LKTK_MARKER = 0 %}",
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
        # no template
        ("select 1", "select 1", []),
        (
            """\
select
  {% set LKTK_MARKER = 0 %}{{ a }}{% set LKTK_MARKER = 0 %},
  {% set LKTK_MARKER = 1 %} {{ b }} {% set LKTK_MARKER = 1 %},
""",
            """\
select
  {{ A }},
  {{ B }},
""",
            ["{{ A }}", "{{ B }}"],
        ),
        (
            """\
select
  {% set LKTK_MARKER = 0 %}{{ a }}
  {% set LKTK_MARKER = 0 %},
  {% set LKTK_MARKER = 1 %} {{ b }}
  {% set LKTK_MARKER = 1 %},
""",
            """\
select
  {{ A }},
  {{ B }},
""",
            ["{{ A }}", "{{ B }}"],
        ),
        (
            """\
select
  {% set LKTK_MARKER = 0 %}
  {{ a }}{% set LKTK_MARKER = 0 %},
  {% set LKTK_MARKER = 1 %}
  {{ b }} {% set LKTK_MARKER = 1 %},
""",
            """\
select
  {{ A }},
  {{ B }},
""",
            ["{{ A }}", "{{ B }}"],
        ),
        (
            """\
select
  {% set LKTK_MARKER = 0 %}
  {{ a }}
  {% set LKTK_MARKER = 0 %},
  {% set LKTK_MARKER = 1 %}
  {{ b }}
  {% set LKTK_MARKER = 1 %},
""",
            """\
select
  {{ A }},
  {{ B }},
""",
            ["{{ A }}", "{{ B }}"],
        ),
        (
            """\
select {% set LKTK_MARKER = 0 %}
  {{ a }}
  {% set LKTK_MARKER = 0 %}, {% set LKTK_MARKER = 1 %}
  {{ b }}
  {% set LKTK_MARKER = 1 %},
""",
            """\
select
  {{ A }},
  {{ B }},
""",
            ["{{ A }}", "{{ B }}"],
        ),
    ],
    ids=utils.shorten,
)
def test_to_liquid(jinja: str, liquid: str, tags: list[str]) -> None:
    res = to_liquid(jinja, tags)
    assert res == liquid
