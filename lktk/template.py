import re
from dataclasses import dataclass

LIQUID_MARKER = "{{% set lktk = {} %}}"
TAG = re.compile(r"""\{%-?\s*([a-z]*)([^"'}]*|'[^']*?'|"[^"]*?")*?-?%\}""")


@dataclass
class LiquidTempate:
    liquid: str
    id: int  # 1-based


def to_jinja(sql: str) -> tuple[str, list[LiquidTempate]]:
    processed = ""
    liquids: list[LiquidTempate] = []
    id_ = 0

    while True:
        id_ += 1
        match = TAG.search(sql)
        if match is None:
            processed += sql
            break

        leading = sql[: match.start()]
        trailing = sql[match.end() :]
        liquid = match.group(0)
        statement = match.group(1)
        marker = LIQUID_MARKER.format(id_)
        processed += f"{leading}{marker}{{% {statement} %}}{marker}"
        sql = trailing
        liquids.append(LiquidTempate(liquid, id_))

    return processed, liquids


def to_liquid(sql: str) -> str:
    # TODO
    return sql
