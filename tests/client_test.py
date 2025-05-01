import pytest
from flaky import flaky

from beaker import Beaker
from beaker.config import InternalConfig


@flaky  # this can fail if the request to GitHub fails
def test_warn_for_newer_version(monkeypatch):
    import beaker.client
    import beaker.version

    InternalConfig().save()

    monkeypatch.setattr(Beaker, "CLIENT_VERSION", "1.0.0")
    monkeypatch.setattr(beaker.client, "_LATEST_VERSION_CHECKED", False)

    with pytest.warns(UserWarning, match="Please upgrade with"):
        Beaker.from_env()

    # Shouldn't warn a second time.
    Beaker.from_env()


def test_str_method(client: Beaker):
    str(client)
