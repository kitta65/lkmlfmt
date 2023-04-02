import pytest

from lktk.formatter import LkmlFormatter
from lktk.parser import parse
from tests import utils


@pytest.mark.parametrize(
    "input_, output",
    [
        ("", ""),
        (
            """key1: value1 key2: 3.14""",
            """\
key1: value1
key2: 3.14""",
        ),
        # ident
        (
            """key1: parent . child key2: value *""",
            """\
key1: parent.child
key2: value*""",
        ),
        # arr
        (
            """values: []""",
            """values: []""",
        ),
        (
            """values: [ value ]""",
            """values: [ value ]""",
        ),
        (
            """values: [ value1, value2, [value3, value4], [value5] ]""",
            """values: [
  value1,
  value2,
  [
    value3,
    value4
  ],
  [ value5 ]
]""",
        ),
        # dict
        (
            """dict: {}""",
            """dict: {}""",
        ),
        (
            """dict: { key: value }""",
            """dict: {
  key: value
}""",
        ),
        (
            """dict: {
  key1: {key2: value2 key3: value3}
}""",
            """\
dict: {
  key1: {
    key2: value2
    key3: value3
  }
}""",
        ),
        # named dict
        (
            """dict: ident {
  key1: ident1 {}
  key2: ident2 { key3: ident3 { } }
}""",
            """\
dict: ident {
  key1: ident1 {}
  key2: ident2 {
    key3: ident3 {}
  }
}""",
        ),
        # leading comments
        ("# eof", "# eof"),
        (
            """\
# comment 1
key1: value1
# comment 2.1
# comment 2.2
key2: value2""",
            """\
# comment 1
key1: value1
# comment 2.1
# comment 2.2
key2: value2""",
        ),
        (
            """\
# comment a
sql_a: code a ;;
# comment b.1
# comment b.2
sql_b: code b ;;""",
            """\
# comment a
sql_a: code a ;;
# comment b.1
# comment b.2
sql_b: code b ;;""",
        ),
        (
            """\
# comment 
key: value""",  # noqa: W291
            """\
# comment
key: value""",
        ),
        (
            """\
key: [
  # this is comment
  ident
]""",
            """\
key: [
  # this is comment
  ident
]""",
        ),
        # trailing comments
        ("key: value # comment", "key: value # comment"),
        (
            """\
key: { # comment
  key: pair
}""",
            """\
key: { # comment
  key: pair
}""",
        ),
        # sql
        (
            """\
sql:     select     
1     ;;""",  # noqa: W291
            """sql: select 1 ;;""",
        ),
        (
            """\
sql:     1     
+     1     ;;""",  # noqa: W291
            """sql: 1 + 1 ;;""",
        ),
        (
            """\
sql:
-- comment
select 1
;;""",
            """\
sql:
  -- comment
  select 1
;;""",
        ),
        (
            """\
sql:
  select '''multiline string

'''
;;""",
            """\
sql:
  select '''multiline string

'''
;;""",
        ),
        (
            """\
sql:
  with temp as (
    select ts, col1, col2, col3
    from
      {% if ts_date._in_query %}${daily.SQL_TABLE_NAME}
      {% elsif ts_week._in_query %}${weekly.SQL_TABLE_NAME}
      {% else %}${monthly.SQL_TABLE_NAME}
      {% endif %}
  )
  select *
  from temp
  where staff_id = '{{ _user_attributes['staff_id'] }}'
;;""",
            """\
sql:
  with
    temp as (
      select ts, col1, col2, col3
      from
        {% if ts_date._in_query %} ${daily.SQL_TABLE_NAME}
        {% elsif ts_week._in_query %} ${weekly.SQL_TABLE_NAME}
        {% else %} ${monthly.SQL_TABLE_NAME}
        {% endif %}
    )
  select *
  from temp
  where staff_id = '{{ _user_attributes['staff_id'] }}'
;;""",
        ),
        # html
        (  # NOTE currently no operation
            """html: <img src="https://example.com/images/{{ value }}.jpg"/> ;;""",
            """html: <img src="https://example.com/images/{{ value }}.jpg"/> ;;""",
        ),
    ],
    ids=utils.shorten,
)
def test_formatter(input_: str, output: str) -> None:
    # once formatted text matches expected output
    tree1, comments = parse(input_, set_parent=True)
    text1 = LkmlFormatter(tree1, comments).fmt()
    assert text1 == output

    # twice formatted text also matches expected output
    tree2, comments = parse(text1, set_parent=True)
    text2 = LkmlFormatter(tree2, comments).fmt()
    assert text2 == output
