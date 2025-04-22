import base64
import re
import time
import warnings
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Set, Tuple, Type, TypeVar, Union

from .aliases import PathOrStr
from .exceptions import RequestException

BUG_REPORT_URL = (
    "https://github.com/allenai/beaker-py/issues/new?assignees=&labels=bug&template=bug_report.yml"
)

_VALIDATION_WARNINGS_ISSUED: Set[Tuple[str, str]] = set()


def issue_data_model_warning(cls: Type, key: str, value: Any):
    warn_about = (cls.__name__, key)
    if warn_about not in _VALIDATION_WARNINGS_ISSUED:
        _VALIDATION_WARNINGS_ISSUED.add(warn_about)
        warnings.warn(
            f"Found unknown field '{key}: {value}' for data model '{cls.__name__}'. "
            "This may be a newly added field that hasn't been defined in beaker-py yet. "
            "Please submit an issue report about this here:\n"
            f"{BUG_REPORT_URL}",
            RuntimeWarning,
        )


def to_lower_camel(s: str) -> str:
    """
    Convert a snake-case string into lower camel case.
    """
    parts = s.split("_")
    out = parts[0] + "".join([p.title() for p in parts[1:]])
    out = re.sub(r"(^|[a-z0-9])Id($|[A-Z0-9])", r"\g<1>ID\g<2>", out)
    return out


def to_snake_case(s: str) -> str:
    """
    Convert a lower camel case strings into snake case.
    """
    if s.islower():
        return s
    s = re.sub(r"(^|[a-z0-9])ID", r"\g<1>Id", s)
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

    def ttl_cached_property(prop) -> property:
        @property  # type: ignore[misc]
        def prop_with_cache(self):
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

        return prop_with_cache  # type: ignore[return-value]

    return ttl_cached_property


def format_since(since: Union[datetime, timedelta, str]) -> str:
    if isinstance(since, datetime):
        if since.tzinfo is not None:
            # Convert to UTC.
            since = since.astimezone(timezone.utc)
        return since.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    elif isinstance(since, timedelta):
        return format_since(datetime.now(tz=timezone.utc) - abs(since))
    else:
        return since


def parse_duration(dur: str) -> int:
    """
    Parse a duration string into nanoseconds.
    """
    dur_normalized = dur.replace(" ", "").lower()
    match = re.match(r"^([0-9.e-]+)([a-z]*)$", dur_normalized)
    if not match:
        raise ValueError(f"invalid duration string '{dur}'")

    value_str, unit = match.group(1), match.group(2)
    try:
        value = float(value_str)
    except ValueError:
        raise ValueError(f"invalid duration string '{dur}'")

    if not unit:
        # assume seconds
        unit = "s"

    if unit in ("ns", "nanosecond", "nanoseconds"):
        # nanoseconds
        return int(value)
    elif unit in ("µs", "microsecond", "microseconds"):
        return int(value * 1_000)
    elif unit in ("ms", "millisecond", "milliseconds"):
        # milliseconds
        return int(value * 1_000_000)
    elif unit in ("s", "sec", "second", "seconds"):
        # seconds
        return int(value * 1_000_000_000)
    elif unit in ("m", "min", "minute", "minutes"):
        # minutes
        return int(value * 60_000_000_000)
    elif unit in ("h", "hr", "hour", "hours"):
        # hours
        return int(value * 3_600_000_000_000)
    else:
        raise ValueError(f"invalid duration string '{dur}'")


TIMESTAMP_RE = re.compile(rb"^([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+Z)(.*)$")


def split_timestamp(s: bytes) -> Optional[str]:
    match = TIMESTAMP_RE.match(s)
    if match is not None:
        return match.group(1).decode()
    else:
        return None


def log_and_wait(retries_so_far: int, err: Exception) -> None:
    from .client import Beaker

    retry_in = min(Beaker.BACKOFF_FACTOR * (2**retries_so_far), Beaker.BACKOFF_MAX)
    Beaker.logger.debug("Request failed with: %s\nRetrying in %d seconds...", err, retry_in)
    time.sleep(retry_in)


def retriable(
    on_failure: Optional[Callable[..., None]] = None,
    recoverable_errors: Tuple[Type[Exception], ...] = (RequestException,),
):
    """
    Use to make a service client method more robust by allowing retries.
    """

    def parametrize_decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def retriable_method(*args, **kwargs) -> T:
            from .client import Beaker

            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except recoverable_errors as err:
                    if retries < Beaker.MAX_RETRIES:
                        if on_failure is not None:
                            on_failure()
                        log_and_wait(retries, err)
                        retries += 1
                    else:
                        raise

        return retriable_method

    return parametrize_decorator


def format_cursor(cursor: int) -> str:
    if cursor < 0:
        raise ValueError("cursor must be >= 0")

    return base64.urlsafe_b64encode(cursor.to_bytes(8, "little")).decode()


def protobuf_to_json_dict(data) -> Dict[str, Any]:
    from google.protobuf.json_format import MessageToDict

    return MessageToDict(data)
