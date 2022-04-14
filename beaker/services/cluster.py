from typing import Union

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class ClusterClient(ServiceClient):
    """
    Accessed via :data:`Beaker.cluster <beaker.Beaker.cluster>`.
    """

    def get(self, cluster: str) -> Cluster:
        """
        Get information about the cluster.

        :param cluster: The cluster name or ID.

        :raises ClusterNotFound: If the cluster doesn't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """

        def _get(id: str) -> Cluster:
            return Cluster.from_json(
                self.request(
                    f"clusters/{id}",
                    exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(id))},
                ).json()
            )

        try:
            # Could be a cluster ID, so we try that first before trying to resolve the name.
            return _get(cluster)
        except ClusterNotFound:
            try:
                cluster_name = self.resolve_cluster_name(cluster)
                return _get(cluster_name)
            except (ValueError, OrganizationNotSet, ClusterNotFound):
                # If the name was invalid, we'll just raise the original error.
                pass
            raise

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

        :param name: The name to assign to the new cluster.
            If :data:`Config.default_org <beaker.Config.default_org>` is not set,
            the name should start with the name of an organization:
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
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        organization, cluster_name = self.resolve_cluster_name(name).split("/", 1)

        if not cpus and not gpus and not gpu_type and not memory:
            raise ValueError("Cloud clusters must specify at least 1 resource")

        return Cluster.from_json(
            self.request(
                f"clusters/{self.url_quote(organization)}",
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
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        cluster_name = self.resolve_cluster(cluster).full_name
        return Cluster.from_json(
            self.request(
                f"clusters/{cluster_name}",
                method="PATCH",
                data={"capacity": max_size},
                exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(cluster_name))},
            ).json()
        )

    def delete(self, cluster: Union[str, Cluster]):
        """
        Delete a cluster.

        :param cluster: The cluster ID, full name, or object.

        :raises ClusterNotFound: If the cluster doesn't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        cluster_name = self.resolve_cluster(cluster).full_name
        self.request(
            f"clusters/{cluster_name}",
            method="DELETE",
            exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(cluster_name))},
        )

    def list(self, org: Optional[Union[str, Organization]] = None) -> List[Cluster]:
        """
        List clusters under an organization.

        :param org: The organization name or object. If not specified,
            :data:`Beaker.config.default_org <beaker.Config.default_org>` is used.

        :raises OrganizationNotFound: If the organization doesn't exist.
        :raises OrganizationNotSet: If neither ``org`` nor
            :data:`Beaker.config.default_org <beaker.Config.default_org>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        org: Organization = self.resolve_org(org)
        return [
            Cluster.from_json(d)
            for d in self.request(
                f"clusters/{org.id}",
                method="GET",
                exceptions_for_status={404: OrganizationNotFound(org.id)},
            ).json()["data"]
        ]

    def nodes(self, cluster: Union[str, Cluster]) -> List[Node]:
        """
        List the nodes in a cluster.

        :param cluster: The cluster ID, full name, or object.

        :raises ClusterNotFound: If the cluster doesn't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        cluster_name = self.resolve_cluster(cluster).full_name
        return [
            Node.from_json(d)
            for d in self.request(
                f"clusters/{cluster_name}/nodes",
                method="GET",
                exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(cluster_name))},
            ).json()["data"]
        ]

    def utilization(self, cluster: Union[str, Cluster]) -> List[NodeUtilization]:
        """
        Get current utilization stats for each node in a cluster.

        :param cluster: The cluster ID, full name, or object.

        :raises ClusterNotFound: If the cluster doesn't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        cluster: Cluster = self.resolve_cluster(cluster)
        nodes = self.nodes(cluster)
        out: List[NodeUtilization] = []
        for node in nodes:
            gpus_used = 0
            cpus_used = 0.0
            for job in self.beaker.job.list(node=node, finalized=False):
                if job.requests is not None:
                    if job.requests.gpu_count is not None:
                        gpus_used += job.requests.gpu_count
                    if job.requests.cpu_count is not None:
                        cpus_used += job.requests.cpu_count
            used = NodeSpecUtil(
                gpu_count=None if node.limits.gpu_count is None else gpus_used,
                cpu_count=None if node.limits.cpu_count is None else cpus_used,
            )
            free = NodeSpecUtil(
                gpu_count=None
                if node.limits.gpu_count is None
                else node.limits.gpu_count - gpus_used,
                cpu_count=None
                if node.limits.cpu_count is None
                else node.limits.cpu_count - cpus_used,
            )
            out.append(
                NodeUtilization(
                    id=node.id,
                    hostname=node.hostname,
                    limits=node.limits,
                    used=used,
                    free=free,
                )
            )
        return out

    def filter_available(
        self, resources: TaskResources, *clusters: Union[str, Cluster]
    ) -> List[Cluster]:
        """
        Filter clusters with enough free resources to run a job with the requested resources.

        :param resources: The requested task resources.
        :param clusters: Clusters to inspect and filter.

        :raises ClusterNotFound: If one of the clusters doesn't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """

        def is_compat(node_spec: Union[NodeSpec, NodeShape, NodeSpecUtil]) -> bool:
            if resources.gpu_count and (
                node_spec.gpu_count is None or node_spec.gpu_count < resources.gpu_count
            ):
                return False
            if resources.cpu_count and (
                node_spec.cpu_count is None or node_spec.cpu_count < resources.cpu_count
            ):
                return False
            # TODO: check memory too
            return True

        available: List[Cluster] = []
        for cluster_ in clusters:
            cluster: Cluster = self.resolve_cluster(cluster_)

            if cluster.node_shape is not None and not is_compat(cluster.node_shape):
                continue

            node_utilization = self.utilization(cluster)
            if cluster.autoscale and len(node_utilization) < cluster.capacity:
                available.append(cluster)
            else:
                for node_util in node_utilization:
                    if is_compat(node_util.free):
                        available.append(cluster)
                        break

        return available

    def _not_found_err_msg(self, cluster: str) -> str:
        return (
            f"'{cluster}': Make sure you're using a valid ID or *full* name of the cluster "
            f"(with the organization prefix, e.g. 'org/cluster_name')"
        )
