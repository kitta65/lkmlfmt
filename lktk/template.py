import re

from lktk.exception import LktkException

LIQUID_MARKER = "{{% set LKTK_MARKER = {} %}}"
TEMPLATE = re.compile(
    r"""(?P<tag>\{%-?\s*(?P<type>#|([a-z]*))([^"'}]*|'[^']*?'|"[^"]*?")*?-?%\})"""
    + r"""|(?P<obj>\{\{([^"'}]*|'[^']*?'|"[^"]*?")*?\}\})"""
    + r"""|(?P<looker>\$\{[^}]*?\})""",
)
DUMMY = re.compile(r"^(?P<lead_n> *?\n)?(?P<indent> *)")


def to_jinja(liquid: str) -> tuple[str, list[str]]:
    jinja = ""
    templates = []
    id_ = 0
    skip_to: str | None = None

    while True:
        match = TEMPLATE.search(liquid)
        if match is None:
            jinja += liquid
            break

        type_ = match.group("type")
        if skip_to is not None and skip_to != type_:
            jinja += liquid[: match.end()]
            templates.append(match.group(0))
            liquid = liquid[match.end() :]
            continue

        skip_to = None
        match type_:
            # control flow https://shopify.github.io/liquid/tags/control-flow/
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
            # iteration https://shopify.github.io/liquid/tags/iteration/
            case "for":
                dummy = "{% for i in [] %}"
            case "cycle":
                dummy = "{{ var }}"
            case "tablerow":
                dummy = "{% for i in [] %}"
            case "endtablerow":
                dummy = "{% endfor %}"
            # template https://shopify.github.io/liquid/tags/template/
            case "comment":
                dummy = "{% if False %}{% raw %}"
                skip_to = "endcomment"
            case "endcomment":
                dummy = "{% endraw %}{% endif %}"
            case "#":
                dummy = "{% set x = 'x' %}"
            case "liquid":
                dummy = "{% set x = 'x' %}"
            case "echo":
                dummy = "{{ var }}"
            case "raw":
                dummy = "{% raw %}"
                skip_to = "endraw"
            case "endraw":
                dummy = "{% endraw %}"
            case "render" | "include":
                dummy = "{% set x = 'x' %}"
            # variable https://shopify.github.io/liquid/tags/variable/
            case "assign":
                dummy = "{% set x = 'x' %}"
            case "capture":
                dummy = "{% set var %}"
            case "endcapture":
                dummy = "{% endset %}"
            case "increment" | "decrement":
                dummy = "{{ var }}"
            # looker
            # https://cloud.google.com/looker/docs/liquid-variable-reference#liquid_variable_definitions
            case "date_start" | "date_end":
                dummy = "{{ var }}"
            case "condition":
                dummy = "{% filter upper %}"
            case "endcondition":
                dummy = "{% endfilter %}"
            case "parameter":
                dummy = "{{ var }}"
            # {{...}} or ${...}
            case None:
                dummy = "{{ var }}"
            # default
            case _:
                dummy = f"{{% {type_} %}}"

        # append results
        marker = LIQUID_MARKER.format(id_)
        jinja += f"{liquid[: match.start()]}{marker}{dummy}{marker}"
        templates.append(match.group(0))

        # prepare for next iteration
        liquid = liquid[match.end() :]
        id_ += 1

    return jinja, templates


def to_liquid(jinja: str, tags: list[str]) -> str:
    for i, tag in enumerate(tags):
        leading, dummy, trailing, *_ = jinja.split(LIQUID_MARKER.format(i))
        match = DUMMY.match(dummy)
        if match is None:
            raise LktkException()

        if match.group("lead_n") is not None:
            leading = leading.rstrip("\n ") + "\n"
            tag = match.group("indent") + tag

        jinja = leading + tag + trailing
    return jinja
