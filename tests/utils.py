import re
from typing import Any

WS = re.compile(r"\s+")


def shorten(arg: Any) -> str:
    if isinstance(arg, str):
        return WS.sub(" ", arg)

    if isinstance(arg, list):
        return " ".join(map(shorten, arg))

    return str(arg)
