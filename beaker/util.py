from pathlib import Path

from .aliases import PathOrStr


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


def path_is_relative_to(path: Path, other: PathOrStr) -> bool:
    """
    This is copied from :meth:`pathlib.PurePath.is_relative_to` to support older Python
    versions (before 3.9, when this method was introduced).
    """
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False
