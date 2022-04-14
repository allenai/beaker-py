from beaker import Beaker


def test_organization_get(client: Beaker, beaker_org_name: str):
    org = client.organization.get(beaker_org_name)
    assert org.name == beaker_org_name
    # Now get by ID.
    client.organization.get(org.id)


def test_organization_list_members(client: Beaker, beaker_org_name: str):
    client.organization.list_members(beaker_org_name)


def test_organization_get_member(client: Beaker):
    client.organization.get_member(client.account.name)
