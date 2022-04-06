from beaker import Beaker


def test_organization_get(client: Beaker, beaker_org_name: str):
    assert client.organization.get(beaker_org_name).name == beaker_org_name


def test_organization_list_members(client: Beaker, beaker_org_name: str):
    client.organization.list_members(beaker_org_name)


def test_organization_get_member(client: Beaker, beaker_org_name: str):
    client.organization.get_member(beaker_org_name, client.account.name)
