from cachetools import TTLCache, cached

from ..data_model import *
from .service_client import ServiceClient


class AccountClient(ServiceClient):
    @cached(cache=TTLCache(maxsize=10, ttl=5 * 60))
    def whoami(self) -> Account:
        """
        Check who you are authenticated as.
        """
        return Account.from_json(self.request("user").json())
