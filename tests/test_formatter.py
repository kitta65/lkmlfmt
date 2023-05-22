import pytest

from lkmlfmt.formatter import fmt
from tests import utils


@pytest.mark.parametrize(
    "input_, output",
    [
        ("", "\n"),
        (
            """\
key1: value1 key2: 3.14 key3: "this is string"
""",
            """\
key1: value1
key2: 3.14
key3: "this is string"
""",
        ),
        (
            """\
include: "path"

  
key: value
""",  # noqa: W293
            """\
include: "path"


key: value
""",
        ),
        # ident
        (
            """\
key1: parent . child key2: value *
""",
            """\
key1: parent.child
key2: value*
""",
        ),
        # string
        (
            """\
dict: {
  str: "
multiline
string"
}
""",
            """\
dict: {
  str: "
multiline
string"
}
""",
        ),
        # arr
        (
            """\
values: []
""",
            """\
values: []
""",
        ),
        (
            """\
values: [ value ]
""",
            """\
values: [ value ]
""",
        ),
        (
            """\
values: [ value1, value2, [value3, value4], [value5] ]
""",
            """\
values: [
  value1,
  value2,
  [
    value3,
    value4,
  ],
  [ value5 ],
]
""",
        ),
        (
            """\
values: [
  value_a1, value_a2,

  value_b1, value_b2,
]
""",
            """\
values: [
  value_a1,
  value_a2,

  value_b1,
  value_b2,
]
""",
        ),
        # dict
        (
            """\
dict: {}
""",
            """\
dict: {}
""",
        ),
        (
            """\
dict: { key: value }
""",
            """\
dict: {
  key: value
}
""",
        ),
        (
            """\
dict: {
  key1: value1


  key2: value2
}
""",
            """\
dict: {
  key1: value1


  key2: value2
}
""",
        ),
        (
            """\
dict: {
  key1: {key2: value2 key3: value3}
}
""",
            """\
dict: {
  key1: {
    key2: value2
    key3: value3
  }
}
""",
        ),
        # named dict
        (
            """\
dict: ident {
  key1: ident1 {}
  key2: ident2 { key3: ident3 { } }
}
""",
            """\
dict: ident {
  key1: ident1 {}
  key2: ident2 {
    key3: ident3 {}
  }
}
""",
        ),
        (  # this may be invalid syntax
            """\
key: [
  ident {},
  ident {},
]
""",
            """\
key: [
  ident {},
  ident {},
]
""",
        ),
        # leading comments
        ("# eof", "# eof\n"),
        ("# eof ", "# eof\n"),
        (
            """\
# comment 1
key1: value1
# comment 2.1
# comment 2.2
key2: value2
""",
            """\
# comment 1
key1: value1
# comment 2.1
# comment 2.2
key2: value2
""",
        ),
        (
            """\
# comment a
sql_a: code a ;;
# comment b.1
# comment b.2
sql_b: code b ;;
""",
            """\
# comment a
sql_a: code a ;;
# comment b.1
# comment b.2
sql_b: code b ;;
""",
        ),
        (
            """\
# comment 
key: value
""",  # noqa: W291
            """\
# comment
key: value
""",
        ),
        (
            """\
key: [
  # this is comment
  ident
]
""",
            """\
key: [
  # this is comment
  ident,
]
""",
        ),
        # trailing comments
        ("key: value # comment", "key: value # comment\n"),
        (
            """\
key: { # comment
  key: pair
}
""",
            """\
key: { # comment
  key: pair
}
""",
        ),
        (
            """\
arr: [
  value1,
  value2 # comment
]
""",
            """\
arr: [
  value1,
  value2, # comment
]
""",
        ),
        # sql
        (
            """\
sql:     select     
1     ;;
""",  # noqa: W291
            """\
sql: select 1 ;;
""",
        ),
        (
            """\
sql:     1     
+     1     ;;
""",  # noqa: W291
            """\
sql: 1 + 1 ;;
""",
        ),
        (
            """\
sql:
-- comment
select 1
;;
""",
            """\
sql:
  -- comment
  select 1
;;
""",
        ),
        (
            """\
dict: {
  sql:
    -- comment
    select 1
  ;;
}
""",
            """\
dict: {
  sql:
    -- comment
    select 1
  ;;
}
""",
        ),
        (
            """\
sql:
  select '''multiline string

'''
;;
""",
            """\
sql:
  select '''multiline string

'''
;;
""",
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
;;
""",
            # TODO
            # ${daily.SQL_TABLE_NAME} and ${weekly.SQL_TABLE_NAME} should be indented
            # latest sqlfmt (>= 0.18.0) do so
            """\
sql:
  with
    temp as (
      select ts, col1, col2, col3
      from
        {% if ts_date._in_query %}
        ${daily.SQL_TABLE_NAME}
        {% elsif ts_week._in_query %}
        ${weekly.SQL_TABLE_NAME}
        {% else %} ${monthly.SQL_TABLE_NAME}
        {% endif %}
    )
  select *
  from temp
  where staff_id = '{{ _user_attributes['staff_id'] }}'
;;
""",
        ),
        (
            """\
sql:
  create or replace model modelname
  options (
    foo="bar"
  ) as
  select * tablename
;;
""",  # statement which is not supported by sqlfmt
            """\
sql:
  create or replace model modelname
  options (
    foo="bar"
  ) as
  select * tablename
;;
""",
        ),
        # template
        # TODO
        # (
        #     """sql: {{   var   }} ;;""",
        #     """sql: {{ var }} ;;""",
        # ),
        # (
        #     """sql: {{ foo . var }} ;;""",
        #     """sql: {{ foo.var }} ;;""",
        # ),
        # (
        #     """sql: {{ "foo" | append : "bar" }} ;;""",
        #     """sql: {{ "foo" | append: "bar" }} ;;""",
        # ),
        # expression
        (
            """\
expression: case(when(yes, "case when yes"), when(no, "case when no"), "else") ;;
""",
            """\
expression:
  case(
    when(yes, "case when yes"),
    when(no, "case when no"),
    "else"
  )
;;
""",  # `no` seems to be not reserved keyword
        ),
        (
            """\
expression: "abc
" = "abc
";;
""",
            """\
expression:
  "abc
" = "abc
"
;;
""",
        ),
        (
            """\
expression:
  NOT yes
  AND "not and or" = ""
  OR no
;;
""",
            """\
expression: NOT yes AND "not and or" = "" OR no ;;
""",
        ),
        # html
        (
            """\
html: <img src="https://example.com/images/{{ value }}.jpg"/> ;;
""",
            """\
html: <img src="https://example.com/images/{{ value }}.jpg"/> ;;
""",
        ),
        (
            """\
dict: {
html:
<div>
<img src="https://example.com/images/{{ value }}.jpg"/>
</div>
;;
}
""",
            """\
dict: {
  html:
    <div>
<img src="https://example.com/images/{{ value }}.jpg"/>
</div>
  ;;
}
""",  # this is not pretty but expected behaviour w/o plugins
        ),
    ],
    ids=utils.shorten,
)
def test_formatter_polyglot(input_: str, output: str) -> None:
    # once formatted text matches expected output
    text1 = fmt(input_, clickhouse=False, plugins=[])
    assert text1 == output

    # twice formatted text also matches expected output
    text2 = fmt(text1, clickhouse=False, plugins=[])
    assert text2 == output


@pytest.mark.parametrize(
    "input_, output",
    [
        (
            "sql: select camelCase from UPPER_CASE ;;\n",
            "sql: select camelCase from UPPER_CASE ;;\n",
        ),
    ],
    ids=utils.shorten,
)
def test_formatter_clickhouse(input_: str, output: str) -> None:
    # once formatted text matches expected output
    text1 = fmt(input_, clickhouse=True, plugins=[])
    assert text1 == output

    # twice formatted text also matches expected output
    text2 = fmt(text1, clickhouse=True, plugins=[])
    assert text2 == output
