import logging

# from dataclasses import dataclass
from pathlib import Path

import click

# from lktk.formatter import LkmlFormatter
# from lktk.parser import parse


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="DEBUG",
)
def run(log_level: str) -> None:
    level = getattr(logging, log_level)
    logging.basicConfig(level=level)


# TODO enable alias `fmt`
@click.command()
@click.option("--check", is_flag=True, help="TODO add help message")
@click.option("--diff", is_flag=True, help="TODO add help message")
@click.argument("files", type=click.Path(exists=True), nargs=-1)
def format(check: bool, diff: bool, files: list[Path]) -> None:
    if check:
        click.echo("check")
    if diff:
        click.echo("diff")
    for f in files:
        click.echo(click.format_filename(f))


run.add_command(format)
