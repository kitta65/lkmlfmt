import re

import pytest

from lkmlfmt.template import to_jinja, to_liquid
from tests import utils


@pytest.mark.parametrize(
    "liquid,jinja",
    [
        # no template
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
{% set LKMLFMT_MARKER = 0 %}{% if True %} 1
{% set LKMLFMT_MARKER = 1 %}{% else %} 2
{% set LKMLFMT_MARKER = 2 %}{% endif %}""",
        ),
        # raw
        (
            """\
select {% raw %}
"{{string literal}}"
{% endraw %}
""",
            """\
select {% set LKMLFMT_MARKER = 0 %}{% raw %}
"{{string literal}}"
{% set LKMLFMT_MARKER = 1 %}{% endraw %}
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
select {% set LKMLFMT_MARKER = 0 %}{% set x = 'x' %}""",
        ),
        (
            """\
select {{
  var
}}""",
            """\
select {% set LKMLFMT_MARKER = 0 %}{{ var }}""",
        ),
        (
            """\
select ${
  var
}""",
            """\
select {% set LKMLFMT_MARKER = 0 %}{{ var }}""",
        ),
        # comment
        (
            "select {% # comment %} 1",
            """\
select {% set LKMLFMT_MARKER = 0 %}{% set x = 'x' %} 1""",
        ),
        (
            """\
select {%
  # this
  # is
  # comment
%} 1""",
            """\
select {% set LKMLFMT_MARKER = 0 %}{% set x = 'x' %} 1""",
        ),
        # {{...}}
        (
            "select {{ '1' }}",
            "select {% set LKMLFMT_MARKER = 0 %}{{ var }}",
        ),
        # ${...}
        (
            "select ${x}",
            "select {% set LKMLFMT_MARKER = 0 %}{{ var }}",
        ),
        # @{...}
        (
            "select @{x}",
            "select {% set LKMLFMT_MARKER = 0 %}{{ var }}",
        ),
    ],
    ids=lambda x: re.sub(r"\s+", " ", x),
)
def test_to_jinja_sqlfmt(liquid: str, jinja: str) -> None:
    res, *_ = to_jinja(liquid)
    assert res == jinja


@pytest.mark.parametrize(
    "jinja,liquid,templates,dummies",
    [
        # no template
        ("select 1", "select 1", [], []),
        (
            """\
select {% set LKMLFMT_MARKER = 0 %}{{ a }};
select {% set LKMLFMT_MARKER = 1 %} {{ b }};
""",
            """\
select {{ A }};
select {{ B }};
""",
            ["{{ A }}", "{{ B }}"],
            ["{{ a }}", "{{ b }}"],
        ),
        (
            """\
select
  {% set LKMLFMT_MARKER = 0 %}{{ a }},
  {% set LKMLFMT_MARKER = 1 %} {{ b }},
""",
            """\
select
  {{ A }},
  {{ B }},
""",
            ["{{ A }}", "{{ B }}"],
            ["{{ a }}", "{{ b }}"],
        ),
        (
            """\
select
  {% set LKMLFMT_MARKER = 0 %}
  {{ a }},
  {% set LKMLFMT_MARKER = 1 %}
  {{ b }},
""",
            """\
select
  {{ A }},
  {{ B }},
""",
            ["{{ A }}", "{{ B }}"],
            ["{{ a }}", "{{ b }}"],
        ),
        (
            """\
select {% set LKMLFMT_MARKER = 0 %}
  {{ a }}, {% set LKMLFMT_MARKER = 1 %}
  {{ b }},
""",
            """\
select
  {{ A }},
  {{ B }},
""",
            ["{{ A }}", "{{ B }}"],
            ["{{ a }}", "{{ b }}"],
        ),
        (
            """\
select
  {%
    set LKMLFMT_MARKER = 0
  %}
  {{
    a
  }},
  {% set
    LKMLFMT_MARKER = 1
  %} {{ b }},
""",
            """\
select
  {{ A }},
  {{ B }},
""",
            ["{{ A }}", "{{ B }}"],
            ["{{ a }}", "{{ b }}"],
        ),
    ],
    ids=utils.shorten,
)
def test_to_liquid(
    jinja: str, liquid: str, templates: list[str], dummies: list[str]
) -> None:
    res = to_liquid(jinja, templates, dummies)
    assert res == liquid
