import pytest

from beaker import Beaker


def test_warn_for_newer_version(monkeypatch):
    from beaker import version

    monkeypatch.setattr(version, "VERSION", "0.1.0")

    with pytest.warns(UserWarning, match="Please upgrade with"):
        Beaker.from_env()

    # Shouldn't warn a second time.
    Beaker.from_env()


def test_str_method(client: Beaker):
    str(client)
