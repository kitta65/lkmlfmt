# lkmlfmt
lkmlfmt formats your LookML files including embedded SQL and HTML.

## Installation
```sh
pip install lkmlfmt
```

## CLI
Use `lkmlfmt` command to format your LookML file(s).
For further information, use `--help` option.

```sh
lkmlfmt [OPTIONS] [FILE]...
```

## API
```python
from lkmlfmt import fmt

lkml = fmt("""\
view: view_name {
  derived_table: {
    sql:
    with cte as (
      select column_name from tablename
      where ts between current_date()-7 and current_date())
    select column_name from cte
    ;;
  }
  dimension: column_name {
    html:
{% if value == "foo" %}
<img src="https://example.com/foo"/>
{% else %}
<img src="https://example.com/bar"/>
{% endif %} ;;
  }
}
""")

assert lkml == """\
view: view_name {
  derived_table: {
    sql:
      with
        cte as (
          select column_name
          from tablename
          where ts between current_date() - 7 and current_date()
        )
      select column_name
      from cte
    ;;
  }
  dimension: column_name {
    html:
      {% if value == "foo" %}
        <img src="https://example.com/foo"/>
      {% else %}
        <img src="https://example.com/bar"/>
      {% endif %}
    ;;
  }
}
"""
```

## GitHub Actions
To check if your LookML files are formatted.

```yaml
on: [pull_request]
jobs:
  format-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          # '>=3.11' is required
          python-version: '3.11'

      # you should specify the version of lkmlfmt!
      - run: pip install lkmlfmt
      - run: lkmlfmt --check path/to/lookml/file/or/directory
```

To format arbitrary branch and create pull request.

```yaml
on: [workflow_dispatch]
jobs:
  format-pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          # '>=3.11' is required
          python-version: '3.11'

      # you should specify the version of lkmlfmt!
      - run: pip install lkmlfmt
      - run: lkmlfmt path/to/lookml/file/or/directory

      # check the documentation especially about workflow permissions
      # https://github.com/marketplace/actions/create-pull-request
      - uses: peter-evans/create-pull-request@v5
        with:
          branch: format/${{ github.ref_name }}
```

## Feedback
I'm not ready to accept pull requests, but your feedback is always welcome.
If you find any bugs, please feel free to create an issue.

## See also
lkmlfmt depends on these awesome formatter and indenter.

* [sqlfmt](https://github.com/tconbeer/sqlfmt)
* [djhtml](https://github.com/rtts/djhtml)
