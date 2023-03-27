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
{% set lktk = 1 %}{% if True %}{% set lktk = 1 %} 1
{% set lktk = 2 %}{% else %}{% set lktk = 2 %} 2
{% set lktk = 3 %}{% endif %}{% set lktk = 3 %}""",
        ),
    ],
    ids=lambda x: re.sub(r"\s+", " ", x),
)
def test_to_jinja(input_: str, output: str) -> None:
    res, _ = to_jinja(input_)
    assert res == output
