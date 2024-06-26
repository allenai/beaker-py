import base64
import time

import pytest

from beaker.client import Beaker
from beaker.services.service_client import ServiceClient
from beaker.util import *


@pytest.mark.parametrize(
    "camel_case, snake_case",
    [
        ("hostPath", "host_path"),
        ("fooBarBaz", "foo_bar_baz"),
        ("docker", "docker"),
        ("replicaGroupID", "replica_group_id"),
    ],
)
def test_to_lower_camel_and_back(camel_case: str, snake_case: str):
    assert to_lower_camel(snake_case) == camel_case
    assert to_snake_case(camel_case) == snake_case


def test_cached_property(client: Beaker, alternate_workspace_name):
    class FakeService(ServiceClient):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._x = 0

        @cached_property(ttl=0.5)
        def x(self) -> int:
            self._x += 1
            return self._x

    service_client = FakeService(client)

    assert service_client.x == 1
    assert service_client.x == 1

    time.sleep(1.0)
    assert service_client.x == 2

    client.config.default_workspace = alternate_workspace_name
    assert service_client.x == 3


def test_format_cursor():
    cursor = 100
    formatted = format_cursor(100)
    assert int.from_bytes(base64.urlsafe_b64decode(formatted), "little") == cursor


def test_parse_duration():
    assert parse_duration("1") == 1_000_000_000
    assert parse_duration("1s") == 1_000_000_000
    assert parse_duration("1sec") == 1_000_000_000
    assert parse_duration("1m") == 60 * 1_000_000_000
    assert parse_duration("1h") == 60 * 60 * 1_000_000_000
