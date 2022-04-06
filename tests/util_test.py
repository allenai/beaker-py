import pytest

from beaker.util import *


@pytest.mark.parametrize(
    "camel_case, snake_case",
    [
        ("hostPath", "host_path"),
        ("fooBarBaz", "foo_bar_baz"),
        ("docker", "docker"),
    ],
)
def test_to_lower_camel_and_back(camel_case: str, snake_case: str):
    assert to_lower_camel(snake_case) == camel_case
    assert to_snake_case(camel_case) == snake_case
