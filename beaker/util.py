import time
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Tuple, TypeVar, Union

from .aliases import PathOrStr

if TYPE_CHECKING:
    from .services.service_client import ServiceClient


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


T = TypeVar("T")

_property_cache: "OrderedDict[Tuple[str, str], Tuple[float, Any]]" = OrderedDict()
_property_cache_max_size = 50


def cached_property(ttl: float = 60):
    """
    This is used to create a cached property on a :class:`~beaker.services.service_client.ServiceClient`
    subclass.

    :param ttl: The time-to-live in seconds. The cached value will be evicted from the cache
        after this many seconds to ensure it stays fresh.

    See :meth:`~beaker.services.account.AccountClient.name`, for example.
    """

    def ttl_cached_property(prop: Callable[[Any], T]):
        @property  # type: ignore[misc]
        def prop_with_cache(self: "ServiceClient") -> T:
            key = (prop.__qualname__, repr(self.config))
            cached = _property_cache.get(key)
            if cached is not None:
                time_cached, value = cached
                if time.monotonic() - time_cached <= ttl:
                    return value
            value = prop(self)
            _property_cache[key] = (time.monotonic(), value)
            while len(_property_cache) > _property_cache_max_size:
                _property_cache.popitem(last=False)
            return value

        return prop_with_cache

    return ttl_cached_property


def format_since(since: Union[datetime, timedelta, str]) -> str:
    if isinstance(since, datetime):
        if since.tzinfo is None:
            return since.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            return since.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    elif isinstance(since, timedelta):
        return f"{since.total_seconds()}s"
    else:
        return since
