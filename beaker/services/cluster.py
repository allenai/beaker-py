from typing import Dict, List, Union

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
                data=ClusterSpec(
                    name=cluster_name,
                    capacity=max_size,
                    preemptible=preemptible,
                    spec=NodeResources(
                        cpu_count=cpus, gpu_count=gpus, gpu_type=gpu_type, memory=memory
                    ),
                ),
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
                data=ClusterPatch(capacity=max_size),
                exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(cluster))},
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
            exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(cluster))},
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
                exceptions_for_status={404: ClusterNotFound(self._not_found_err_msg(cluster))},
            ).json()["data"]
        ]

    def utilization(self, cluster: Union[str, Cluster]) -> ClusterUtilization:
        """
        Get current utilization stats for each node in a cluster.

        :param cluster: The cluster ID, full name, or object.

        :raises ClusterNotFound: If the cluster doesn't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        cluster: Cluster = self.resolve_cluster(cluster)
        nodes = self.nodes(cluster)

        running_jobs = 0
        queued_jobs = 0
        node_to_util: Dict[str, Dict[str, Union[int, float]]] = {
            node.id: {"running_jobs": 0, "gpus_used": 0, "cpus_used": 0.0} for node in nodes
        }

        for job in self.beaker.job.list(cluster=cluster, finalized=False):
            if job.status.current == CurrentJobStatus.running:
                running_jobs += 1
            elif job.status.current == CurrentJobStatus.created:
                queued_jobs += 1

            if job.node is not None:
                if job.node not in node_to_util:
                    continue  # unlikely

                node_util = node_to_util[job.node]
                node_util["running_jobs"] += 1
                if job.requests is not None:
                    if job.requests.gpu_count is not None:
                        node_util["gpus_used"] += job.requests.gpu_count
                    if job.requests.cpu_count is not None:
                        node_util["cpus_used"] += job.requests.cpu_count

        return ClusterUtilization(
            cluster=cluster,
            running_jobs=running_jobs,
            queued_jobs=queued_jobs,
            nodes=[
                NodeUtilization(
                    id=node.id,
                    hostname=node.hostname,
                    limits=node.limits,
                    running_jobs=node_to_util[node.id]["running_jobs"],
                    used=NodeResources(
                        gpu_count=None
                        if node.limits.gpu_count is None
                        else min(node.limits.gpu_count, node_to_util[node.id]["gpus_used"]),
                        cpu_count=None
                        if node.limits.cpu_count is None
                        else min(node.limits.cpu_count, node_to_util[node.id]["cpus_used"]),
                        gpu_type=node.limits.gpu_type,
                    ),
                    free=NodeResources(
                        gpu_count=None
                        if node.limits.gpu_count is None
                        else max(0, node.limits.gpu_count - node_to_util[node.id]["gpus_used"]),
                        cpu_count=None
                        if node.limits.cpu_count is None
                        else max(0, node.limits.cpu_count - node_to_util[node.id]["cpus_used"]),
                        gpu_type=node.limits.gpu_type,
                    ),
                )
                for node in nodes
            ],
        )

    def filter_available(
        self, resources: TaskResources, *clusters: Union[str, Cluster]
    ) -> List[ClusterUtilization]:
        """
        Filter out clusters that don't have enough available resources, returning
        a list of :class:`ClusterUtilization <beaker.data_model.cluster.ClusterUtilization>` for each
        cluster that has sufficient resources.

        This can be used, for example, to automatically find an on-premise cluster with enough
        free resources to run a particular task.

        .. caution::
            This method is experimental and may change or be removed in future releases.

        :param resources: The requested resources.
        :param clusters: Clusters to inspect and filter.

        :raises ClusterNotFound: If one of the clusters doesn't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """

        def node_is_compat(node_shape: NodeResources) -> bool:
            if resources.gpu_count and (
                node_shape.gpu_count is None or node_shape.gpu_count < resources.gpu_count
            ):
                return False
            if resources.cpu_count and (
                node_shape.cpu_count is None or node_shape.cpu_count < resources.cpu_count
            ):
                return False
            # TODO: check memory too
            return True

        def cluster_is_available(cluster_: Union[str, Cluster]) -> Optional[ClusterUtilization]:
            cluster: Cluster = self.resolve_cluster(cluster_)

            if cluster.node_shape is not None and not node_is_compat(cluster.node_shape):
                return None

            cluster_utilization = self.utilization(cluster)
            if cluster.autoscale and len(cluster_utilization.nodes) < cluster.capacity:
                available.append(cluster_utilization)
            else:
                for node_util in cluster_utilization.nodes:
                    if node_is_compat(node_util.free):
                        return cluster_utilization

            return None

        available: List[ClusterUtilization] = []

        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for cluster_ in clusters:
                futures.append(executor.submit(cluster_is_available, cluster_))
            for future in concurrent.futures.as_completed(futures):
                cluster_util = future.result()
                if cluster_util is not None:
                    available.append(cluster_util)

        return sorted(available, key=lambda util: (util.queued_jobs, util.running_jobs))

    def url(self, cluster: Union[str, Cluster]) -> str:
        """
        Get the URL for a cluster.

        :param cluster: The cluster ID, full name, or object.

        :raises ClusterNotFound: If the cluster doesn't exist.
        """
        cluster_name = self.resolve_cluster(cluster).full_name
        return f"{self.config.agent_address}/cl/{cluster_name}/details"

    def _not_found_err_msg(self, cluster: Union[str, Cluster]) -> str:
        cluster = cluster if isinstance(cluster, str) else cluster.id
        return (
            f"'{cluster}': Make sure you're using a valid ID or *full* name of the cluster "
            f"(with the organization prefix, e.g. 'org/cluster_name')"
        )
