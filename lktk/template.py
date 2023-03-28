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
        match type_ := match.group(1):
            # control flow
            case "if":
                jinja = "{% if True %}"
            case "elsif":
                jinja = "{% elif True %}"
            case "unless":
                jinja = "{% if True %}"
            case "endunless":
                jinja = "{% endif %}"
            case "case":
                jinja = "{% if True %}"
            case "when":
                jinja = "{% elif True %}"
            case "endcase":
                jinja = "{% endif %}"
            # iteration
            case "for":
                jinja = "{% for i in [] %}"
            case "cycle":
                jinja = "{{ var }}"
            case "tablerow":
                jinja = "{% for i in [] %}"
            case "endtablerow":
                jinja = "{% endfor %}"
            # template
            case "comment":
                jinja = "/*"
            case "endcomment":
                jinja = "*/"
            case "liquid":
                jinja = "{% set x = 'x' %}"
            case "raw":
                jinja = "/*"  # or {{"""
            case "endraw":
                jinja = "*/"  # or """}}
            case "render" | "include":
                jinja = "{% set x = 'x' %}"
            # variable
            case "assign":
                jinja = "{% set x = 'x' %}"
            case "capture":
                jinja = "/*"  # or {{"""
            case "endcapture":
                jinja = "*/"  # or """}}
            case "increment" | "decrement":
                jinja = "{{ var }}"
            # default
            case _:
                jinja = f"{{% {type_} %}}"

        marker = LIQUID_MARKER.format(id_)
        processed += f"{leading}{marker}{jinja}{marker}"
        sql = trailing
        liquids.append(LiquidTempate(liquid, id_))

    return processed, liquids


def to_liquid(sql: str) -> str:
    # TODO
    return sql
