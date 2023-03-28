import re

LIQUID_MARKER = "{{% set lktk = {} %}}"
TAG = re.compile(r"""\{%-?\s*(#|([a-z]*))([^"'}]*|'[^']*?'|"[^"]*?")*?-?%\}""")


def to_jinja(liquid: str) -> tuple[str, list[str]]:
    jinja = ""
    tags = []
    id_ = 0

    while True:
        match = TAG.search(liquid)
        if match is None:
            jinja += liquid
            break

        leading = liquid[: match.start()]
        trailing = liquid[match.end() :]
        tag = match.group(0)
        match type_ := match.group(1):
            # control flow
            case "if":
                dummy = "{% if True %}"
            case "elsif":
                dummy = "{% elif True %}"
            case "unless":
                dummy = "{% if True %}"
            case "endunless":
                dummy = "{% endif %}"
            case "case":
                dummy = "{% if True %}"
            case "when":
                dummy = "{% elif True %}"
            case "endcase":
                dummy = "{% endif %}"
            # iteration
            case "for":
                dummy = "{% for i in [] %}"
            case "cycle":
                dummy = "{{ var }}"
            case "tablerow":
                dummy = "{% for i in [] %}"
            case "endtablerow":
                dummy = "{% endfor %}"
            # template
            case "comment":
                dummy = "/*"
            case "endcomment":
                dummy = "*/"
            case "liquid":
                dummy = "{% set x = 'x' %}"
            case "raw":
                dummy = "/*"  # or {{"""
            case "endraw":
                dummy = "*/"  # or """}}
            case "render" | "include":
                dummy = "{% set x = 'x' %}"
            # variable
            case "assign":
                dummy = "{% set x = 'x' %}"
            case "capture":
                dummy = "/*"  # or {{"""
            case "endcapture":
                dummy = "*/"  # or """}}
            case "increment" | "decrement":
                dummy = "{{ var }}"
            # comment
            case "#":
                dummy = "{% set x = 'x' %}"
            # default
            case _:
                dummy = f"{{% {type_} %}}"

        marker = LIQUID_MARKER.format(id_)
        jinja += f"{leading}{marker}{dummy}{marker}"
        liquid = trailing
        tags.append(tag)
        id_ += 1

    return jinja, tags


# TODO consider newline between markers
def to_liquid(jinja: str, tags: list[str]) -> str:
    for i, tag in enumerate(tags):
        leading, _, trailing, *_ = jinja.split(LIQUID_MARKER.format(i))
        jinja = leading + tag + trailing
    return jinja
