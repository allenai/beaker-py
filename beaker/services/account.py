from typing import List

from cachetools import TTLCache, cached

from ..data_model import *
from .service_client import ServiceClient


class AccountClient(ServiceClient):
    @property  # type: ignore[misc]
    @cached(cache=TTLCache(maxsize=10, ttl=5 * 60))
    def name(self):
        """
        A convenience property to get username of your Beaker account.
        """
        return self.whoami().name

    def whoami(self) -> Account:
        """
        Check who you are authenticated as.
        """
        return Account.from_json(self.request("user").json())

    def list_organizations(self) -> List[Organization]:
        """
        List all organizations you are a member of.
        """
        return [Organization.from_json(d) for d in self.request("user/orgs").json()["data"]]
