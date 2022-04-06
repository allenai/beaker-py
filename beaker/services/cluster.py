from typing import Union

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class ClusterClient(ServiceClient):
    def create(
        self,
        name: str,
        max_size: int = 1,
        preemptible: bool = False,
        cpus: Optional[float] = None,
        gpus: int = 0,
        gpu_type: Optional[str] = None,
        memory: Optional[str] = None,
    ) -> Cluster:
        """
        Create a new Beaker cloud cluster.

        .. note::
            For creating on-premise clusters you should still use the `Beaker CLI
            <https://github.com/allenai/beaker>`_.

        :param name: The full name to assign to the new cluster. This should be in the form of
            "{organization}/{cluster_name}", e.g. "ai2/my-new-cluster".
        :param max_size: The maximum number of nodes the cluster can scale up to.
        :param preemptible: Use preemptible cloud machines for the nodes.
        :param cpus: The number of virtual CPU available to each node.
        :param gpus: The number of GPUs available to each node.
        :param gpu_type: The type of GPU available to each node.
        :param memory: The amount of memory available to each node, specified as a number
            with a unit suffix. E.g. "2.5GiB".

        :raises ValueError: If the cluster name or requested resources are invalid.
        :raises ClusterConflict: If a cluster by that name already exists.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        try:
            organization, cluster_name = name.split("/")
        except ValueError:
            raise ValueError(
                f"Invalid cluster name '{name}'. "
                "Cluster names must be of the form '{organization}/{name}'."
            )

        if not cpus and not gpus and not gpu_type and not memory:
            raise ValueError("Cloud clusters must specify at least 1 resource")

        return Cluster.from_json(
            self.request(
                f"clusters/{self._url_quote(organization)}",
                method="POST",
                data={
                    "name": cluster_name,
                    "capacity": max_size,
                    "preemptible": preemptible,
                    "spec": NodeSpec(
                        cpu_count=cpus, gpu_count=gpus, gpu_type=gpu_type, memory=memory
                    ).to_json(),
                },
                exceptions_for_status={409: ClusterConflict(cluster_name)},
            ).json()
        )

    def update(self, cluster: Union[str, Cluster], max_size: int) -> Cluster:
        """
        Modify a cluster.

        :param cluster: The cluster ID, full name, or object.
        :param max_size: The maximum number of nodes.

        :raises ClusterNotFound: If the cluster doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        cluster_id = cluster if isinstance(cluster, str) else cluster.id
        self.request(
            f"clusters/{cluster_id}",
            method="PATCH",
            data={"capacity": max_size},
            exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(cluster_id))},
        )
        return self.get(cluster_id)

    def get(self, cluster: str) -> Cluster:
        """
        Get information about the cluster.

        :param cluster: The cluster ID or full name.

        :raises ClusterNotFound: If the cluster doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        return Cluster.from_json(
            self.request(
                f"clusters/{cluster}",
                exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(cluster))},
            ).json()
        )

    def delete(self, cluster: Union[str, Cluster]):
        """
        Delete a cluster.

        :param cluster: The cluster ID, full name, or object.

        :raises ClusterNotFound: If the cluster doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        cluster_id = cluster if isinstance(cluster, str) else cluster.id
        self.request(
            f"clusters/{cluster_id}",
            method="DELETE",
            exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(cluster_id))},
        )

    def list(self, org: Union[str, Organization]) -> List[Cluster]:
        """
        List clusters under an organization.

        :param org: The organization name or object.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org_name = org if isinstance(org, str) else org.name
        return [
            Cluster.from_json(d)
            for d in self.request(
                f"clusters/{self._url_quote(org_name)}",
                method="GET",
                exceptions_for_status={404: OrganizationNotFound(org_name)},
            ).json()["data"]
        ]

    def nodes(self, cluster: Union[str, Cluster]) -> List[Node]:
        """
        List the nodes in a cluster.

        :param cluster: The cluster ID, full name, or object.

        :raises ClusterNotFound: If the cluster doesn't exist.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        cluster_id = cluster if isinstance(cluster, str) else cluster.id
        return [
            Node.from_json(d)
            for d in self.request(
                f"clusters/{cluster_id}/nodes",
                method="GET",
                exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(cluster_id))},
            ).json()["data"]
        ]

    def _not_found_err_msg(self, cluster: str) -> str:
        return (
            f"'{cluster}': Make sure you're using the *full* name of the cluster "
            f"(with the organization prefix, e.g. 'org/cluster_name')"
        )
