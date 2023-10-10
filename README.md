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
      select col1, col2 from tablename
      where ts between current_date()-7 and current_date())
    select {% if true %} col1 {% else %} col2 {% endif %} from cte
    ;;
  }
}
""")

assert lkml == """\
view: view_name {
  derived_table: {
    sql:
      with
        cte as (
          select col1, col2
          from tablename
          where ts between current_date() - 7 and current_date()
        )
      select
        {% if true %} col1
        {% else %} col2
        {% endif %}
      from cte
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
In default, lkmlfmt formats embedded sql using sqlfmt.

* [sqlfmt](https://github.com/tconbeer/sqlfmt)

You can install plugins to change the format of embeded looker expression, sql or html.
They are distributed under their own licenses, so please check if they are suitable for your purpose.

* [lkmlfmt-djhtml](https://github.com/kitta65/lkmlfmt-djhtml)
