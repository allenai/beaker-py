from typing import List, Union

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class OrganizationClient(ServiceClient):
    def get(self, name: str) -> Organization:
        """
        Get information about an organization.

        :param name: The organization name.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        return Organization.from_json(
            self.request(
                f"orgs/{self._url_quote(name)}",
                method="GET",
                exceptions_for_status={404: OrganizationNotFound(name)},
            ).json()
        )

    def add_member(
        self, org: Union[str, Organization], account: Union[str, Account]
    ) -> OrganizationMember:
        """
        Add an account to an organization.

        :param org: The organization name or object.
        :param account: The account name or object.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises AccountNotFound: If the account doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org_name = org if isinstance(org, str) else org.name
        account_name = account if isinstance(account, str) else account.name

        # Check if organization exists.
        self.get(org_name)

        self.request(
            f"orgs/{self._url_quote(org_name)}/members/{account_name}",
            method="PUT",
            exceptions_for_status={404: AccountNotFound(account_name)},
        )
        return self.get_member(org_name, account_name)

    def get_member(
        self, org: Union[str, Organization], account: Union[str, Account]
    ) -> OrganizationMember:
        """
        Get information about an organization member.

        :param org: The organization name or object.
        :param account: The account name or object.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises AccountNotFound: If the account doesn't exist or isn't a member of the org.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org_name = org if isinstance(org, str) else org.name
        account_name = account if isinstance(account, str) else account.name

        # Check if organization exists.
        self.get(org_name)

        return OrganizationMember.from_json(
            self.request(
                f"orgs/{self._url_quote(org_name)}/members/{account_name}",
                method="GET",
                exceptions_for_status={404: AccountNotFound(account_name)},
            ).json()
        )

    def list_members(self, org: Union[str, Organization]) -> List[Account]:
        """
        List members of an organization.

        :param org: The organization name or object.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org_name = org if isinstance(org, str) else org.name

        return [
            Account.from_json(d)
            for d in self.request(
                f"orgs/{self._url_quote(org_name)}/members",
                method="GET",
                exceptions_for_status={404: OrganizationNotFound(org_name)},
            ).json()["data"]
        ]

    def remove_member(self, org: Union[str, Organization], account: Union[str, Account]):
        """
        Remove a member from an organization.

        :param org: The organization name or object.
        :param account: The account name or object.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org_name = org if isinstance(org, str) else org.name
        account_name = account if isinstance(account, str) else account.name

        # Check if organization exists.
        self.get(org_name)

        self.request(
            f"orgs/{self._url_quote(org_name)}/members/{account_name}",
            method="DELETE",
            exceptions_for_status={404: AccountNotFound(account_name)},
        )
