#!/usr/bin/env python3
import os
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]


def toml_version() -> str:
    toml = (PROJECT_ROOT / "pyproject.toml").read_text()
    data = tomllib.loads(toml)
    version = data["tool"]["poetry"]["version"]
    assert isinstance(version, str)
    return version


if __name__ == "__main__":
    tag_version = os.getenv("GITHUB_REF")
    if tag_version is None:
        raise Exception("You have to export GITHUB_REF environment variable.")

    tag_version = tag_version.replace("refs/tags/", "")
    assert toml_version() == tag_version
