import pytest

from beaker import Beaker


def test_warn_for_newer_version(monkeypatch):
    import beaker.client
    import beaker.version

    monkeypatch.setattr(beaker.version, "VERSION", "0.1.0")
    monkeypatch.setattr(beaker.client, "_LATEST_VERSION_CHECKED", False)

    with pytest.warns(UserWarning, match="Please upgrade with"):
        Beaker.from_env()

    # Shouldn't warn a second time.
    Beaker.from_env()


def test_str_method(client: Beaker):
    str(client)
