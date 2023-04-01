import re

LIQUID_MARKER = "{{% set lktk = {} %}}"
TEMPLATE = re.compile(
    r"""(?P<tag>\{%-?\s*(?P<type>#|([a-z]*))([^"'}]*|'[^']*?'|"[^"]*?")*?-?%\})"""
    + r"""|(?P<obj>\{\{([^"'}]*|'[^']*?'|"[^"]*?")*?\}\})""",
)


def to_jinja(liquid: str) -> tuple[str, list[str]]:
    jinja = ""
    templates = []
    id_ = 0

    while True:
        match = TEMPLATE.search(liquid)
        if match is None:
            jinja += liquid
            break

        leading = liquid[: match.start()]
        trailing = liquid[match.end() :]
        template = match.group(0)
        match type_ := match.group("type"):
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
                dummy = "{% if False %}{% raw %}"
            case "endcomment":
                dummy = "{% endraw %}{% endif %}"
            case "liquid":
                dummy = "{% set x = 'x' %}"
            case "echo":
                dummy = "{{ var }}"
            case "raw":
                dummy = "{% raw %}"
            case "endraw":
                dummy = "{% endrow %}"
            case "render" | "include":
                dummy = "{% set x = 'x' %}"
            # variable
            case "assign":
                dummy = "{% set x = 'x' %}"
            case "capture":
                dummy = "{% set var %}"
            case "endcapture":
                dummy = "{% endset %}"
            case "increment" | "decrement":
                dummy = "{{ var }}"
            # comment
            case "#":
                dummy = "{% set x = 'x' %}"
            case None:
                dummy = "{{ var }}"
            # default
            case _:
                dummy = f"{{% {type_} %}}"

        marker = LIQUID_MARKER.format(id_)
        jinja += f"{leading}{marker}{dummy}{marker}"
        liquid = trailing
        templates.append(template)
        id_ += 1

    return jinja, templates


# TODO consider newline between markers
def to_liquid(jinja: str, tags: list[str]) -> str:
    for i, tag in enumerate(tags):
        leading, _, trailing, *_ = jinja.split(LIQUID_MARKER.format(i))
        jinja = leading + tag + trailing
    return jinja
