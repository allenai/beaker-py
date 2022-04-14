from typing import List, Optional, Union

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class OrganizationClient(ServiceClient):
    """
    Accessed via :data:`Beaker.organization <beaker.Beaker.organization>`.
    """

    def get(self, org: Optional[str] = None) -> Organization:
        """
        Get information about an organization.

        :param org: The organization name or ID. If not specified,
            :data:`Beaker.config.default_org <beaker.Config.default_org>` is used.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises OrganizationNotSet: If neither ``org`` nor
            :data:`Beaker.config.default_org <beaker.Config.default_org>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org = org or self.config.default_org
        if org is None:
            raise OrganizationNotSet("'org' argument required since default org not set")

        return Organization.from_json(
            self.request(
                f"orgs/{self.url_quote(org)}",
                method="GET",
                exceptions_for_status={404: OrganizationNotFound(org)},
            ).json()
        )

    def add_member(
        self, account: Union[str, Account], org: Optional[Union[str, Organization]] = None
    ) -> OrganizationMember:
        """
        Add an account to an organization.

        :param account: The account name or object.
        :param org: The organization name or object. If not specified,
            :data:`Beaker.config.default_org <beaker.Config.default_org>` is used.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises OrganizationNotSet: If neither ``org`` nor
            :data:`Beaker.config.default_org <beaker.Config.default_org>` are set.
        :raises AccountNotFound: If the account doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org: Organization = self.resolve_org(org)
        account_name = account if isinstance(account, str) else account.name
        self.request(
            f"orgs/{self.url_quote(org.name)}/members/{account_name}",
            method="PUT",
            exceptions_for_status={404: AccountNotFound(account_name)},
        )
        return self.get_member(account_name, org=org)

    def get_member(
        self, account: Union[str, Account], org: Optional[Union[str, Organization]] = None
    ) -> OrganizationMember:
        """
        Get information about an organization member.

        :param account: The account name or object.
        :param org: The organization name or object. If not specified,
            :data:`Beaker.config.default_org <beaker.Config.default_org>` is used.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises OrganizationNotSet: If neither ``org`` nor
            :data:`Beaker.config.default_org <beaker.Config.default_org>` are set.
        :raises AccountNotFound: If the account doesn't exist or isn't a member of the org.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org: Organization = self.resolve_org(org)
        account_name = account if isinstance(account, str) else account.name
        return OrganizationMember.from_json(
            self.request(
                f"orgs/{self.url_quote(org.name)}/members/{account_name}",
                method="GET",
                exceptions_for_status={404: AccountNotFound(account_name)},
            ).json()
        )

    def list_members(self, org: Optional[Union[str, Organization]] = None) -> List[Account]:
        """
        List members of an organization.

        :param org: The organization name or object. If not specified,
            :data:`Beaker.config.default_org <beaker.Config.default_org>` is used.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises OrganizationNotSet: If neither ``org`` nor
            :data:`Beaker.config.default_org <beaker.Config.default_org>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org: Organization = self.resolve_org(org)
        return [
            Account.from_json(d)
            for d in self.request(
                f"orgs/{self.url_quote(org.name)}/members",
                method="GET",
                exceptions_for_status={404: OrganizationNotFound(org.name)},
            ).json()["data"]
        ]

    def remove_member(
        self, account: Union[str, Account], org: Optional[Union[str, Organization]] = None
    ):
        """
        Remove a member from an organization.

        :param account: The account name or object.
        :param org: The organization name or object. If not specified,
            :data:`Beaker.config.default_org <beaker.Config.default_org>` is used.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises OrganizationNotSet: If neither ``org`` nor
            :data:`Beaker.config.default_org <beaker.Config.default_org>` are set.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org: Organization = self.resolve_org(org)
        account_name = account if isinstance(account, str) else account.name
        self.request(
            f"orgs/{self.url_quote(org.name)}/members/{account_name}",
            method="DELETE",
            exceptions_for_status={404: AccountNotFound(account_name)},
        )
