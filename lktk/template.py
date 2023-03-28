import re

LIQUID_MARKER = "{{% set lktk = {} %}}"
TAG = re.compile(r"""\{%-?\s*(#|([a-z]*))([^"'}]*|'[^']*?'|"[^"]*?")*?-?%\}""")


def to_jinja(sql: str) -> tuple[str, list[str]]:
    processed = ""
    liquids = []
    id_ = 0

    while True:
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
            # comment
            case "#":
                jinja = "{% set x = 'x' %}"
            # default
            case _:
                jinja = f"{{% {type_} %}}"

        marker = LIQUID_MARKER.format(id_)
        processed += f"{leading}{marker}{jinja}{marker}"
        sql = trailing
        liquids.append(liquid)
        id_ += 1

    return processed, liquids


# TODO consider newline between markers
def to_liquid(jinja: str, tags: list[str]) -> str:
    for i, tag in enumerate(tags):
        leading, _, trailing, *_ = jinja.split(LIQUID_MARKER.format(i))
        jinja = leading + tag + trailing
    return jinja
