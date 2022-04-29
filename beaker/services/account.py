from typing import List

from ..data_model import *
from ..exceptions import *
from ..util import cached_property
from .service_client import ServiceClient


class AccountClient(ServiceClient):
    """
    Accessed via :data:`Beaker.account <beaker.Beaker.account>`.
    """

    @cached_property(ttl=3 * 60)
    def name(self) -> str:
        """
        A convenience property to get username of your Beaker account.
        """
        return self.whoami().name

    def whoami(self) -> Account:
        """
        Check who you are authenticated as.

        :raises HTTPError: Any unexpected HTTP exception that can occur.
        """
        return Account.from_json(self.request("user").json())

    def list_organizations(self) -> List[Organization]:
        """
        List all organizations you are a member of.

        :raises HTTPError: Any unexpected HTTP exception that can occur.
        """
        return [Organization.from_json(d) for d in self.request("user/orgs").json()["data"]]

    def get(self, account: str) -> Account:
        """
        Get information about an account.

        :param account: The account name or ID.

        :raises AccountNotFound: If the account doesn't exist.
        :raises HTTPError: Any unexpected HTTP exception that can occur.
        """
        return Account.from_json(
            self.request(
                f"users/{self.url_quote(account)}",
                method="GET",
                exceptions_for_status={404: AccountNotFound(account)},
            ).json()
        )
