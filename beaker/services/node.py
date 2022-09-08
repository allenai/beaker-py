from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class NodeClient(ServiceClient):
    """
    Accessed via :data:`Beaker.node <beaker.Beaker.node>`.
    """

    def get(self, node_id: str) -> Node:
        """
        Get information about a node.

        :param node_id: The ID of the node.

        :raises NodeNotFound: If the node doesn't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises RequestException: Any other exception that can occur when contacting the
            Beaker server.
        """
        return Node.from_json(
            self.request(
                f"nodes/{node_id}",
                exceptions_for_status={404: NodeNotFound(node_id)},
            ).json()
        )
