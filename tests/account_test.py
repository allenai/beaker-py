from beaker.client import Beaker


def test_whoami(client: Beaker):
    client.account.whoami()


def test_name(client: Beaker):
    assert isinstance(client.account.name, str)


def test_list_organizations(client: Beaker):
    client.account.list_organizations()
