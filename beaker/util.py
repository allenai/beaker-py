def to_lower_camel(s: str) -> str:
    """
    Convert a snake-case string into lower camel case.
    """
    parts = s.split("_")
    return parts[0] + "".join([p.title() for p in parts[1:]])


def to_snake_case(s: str) -> str:
    """
    Convert a lower camel case strings into snake case.
    """
    parts = []
    for c in s:
        if c.isupper():
            parts.append("_")
        parts.append(c.lower())
    return "".join(parts)
