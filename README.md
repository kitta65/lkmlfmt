# Looker Toolkit
WIP

## Installation
```sh
pip install lktk
```

## CLI
### format
Use `lktk format` command to format your LookML file(s).
For further information, use `--help` option.

```sh
lktk format [OPTIONS] [FILE]...
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
          python-version: '3.11'
          cache: pip
      - run: pip install
      - run: lktk format --check path/to/lookml/file/or/directory
```

To format specific branch and create pull request.

```yaml
# WIP
on: [workflow_dispatch]
jobs:
  format-pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: pip
      - run: pip install
      - run: lktk format path/to/lookml/file/or/directory
```

## Feedback
I'm not ready to accept pull requests, but your feedback is always welcome.
If you find any bugs, please feel free to create an issue.
