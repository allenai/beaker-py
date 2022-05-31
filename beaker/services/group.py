from typing import Generator, List, Optional, Union

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient


class GroupClient(ServiceClient):
    """
    Accessed via :data:`Beaker.group <beaker.Beaker.group>`.
    """

    def get(self, group: str) -> Group:
        """
        Get info about a group.

        :param group: The group ID or name.

        :raises GroupNotFound: If the group can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """

        def _get(id: str) -> Group:
            return Group.from_json(
                self.request(
                    f"groups/{self.url_quote(id)}",
                    exceptions_for_status={404: GroupNotFound(self._not_found_err_msg(id))},
                ).json()
            )

        try:
            # Could be an ID or full name, so we try that first.
            return _get(group)
        except GroupNotFound:
            if "/" not in group:
                # Now try with adding the account name.
                try:
                    return _get(f"{self.beaker.account.name}/{group}")
                except GroupNotFound:
                    pass
            raise

    def create(
        self,
        name: str,
        *experiments: Union[str, Experiment],
        description: Optional[str] = None,
        workspace: Optional[str] = None,
    ) -> Group:
        """
        :param name: The name to assign the group.
        :param experiments: Experiments to add to the group.
        :param description: Group description.
        :param workspace: The workspace to create the group under. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.

        :raises ValueError: If the name is invalid.
        :raises GroupConflict: If a group with the given name already exists.
        :raises ExperimentNotFound: If any of the given experiments don't exist.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        self.validate_beaker_name(name)
        workspace: Workspace = self.resolve_workspace(workspace)
        exp_ids: List[str] = list(
            set([self.resolve_experiment(experiment).id for experiment in experiments])
        )
        group_data = self.request(
            "groups",
            method="POST",
            data=GroupSpec(
                name=name,
                descriptio=description,
                workspace=workspace.full_name,
                experiments=exp_ids,
            ),
            exceptions_for_status={409: GroupConflict(name)},
        ).json()
        return self.get(group_data["id"])

    def delete(self, group: Union[str, Group]):
        """
        Delete a group.

        :param group: The group ID, name, or object.

        :raises GroupNotFound: If the group can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        group_id = self.resolve_group(group).id
        self.request(
            f"groups/{self.url_quote(group_id)}",
            method="DELETE",
            exceptions_for_status={404: GroupNotFound(self._not_found_err_msg(group))},
        )

    def rename(self, group: Union[str, Group], name: str) -> Group:
        """
        Rename a group.

        :param group: The group ID, name, or object.
        :param name: The new name for the group.

        :raises ValueError: If the new name is invalid.
        :raises GroupNotFound: If the group can't be found.
        :raises GroupConflict: If a group by that name already exists.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        self.validate_beaker_name(name)
        group_id = self.resolve_group(group).id
        return Group.from_json(
            self.request(
                f"groups/{self.url_quote(group_id)}",
                method="PATCH",
                data=GroupPatch(name=name),
                exceptions_for_status={
                    404: GroupNotFound(self._not_found_err_msg(group)),
                    409: GroupConflict(name),
                },
            ).json()
        )

    def add_experiments(self, group: Union[str, Group], *experiments: Union[str, Experiment]):
        """
        Add experiments to a group.

        :param group: The group ID, name, or object.
        :param experiments: Experiments to add to the group.

        :raises GroupNotFound: If the group can't be found.
        :raises ExperimentNotFound: If any of the given experiments don't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        group_id = self.resolve_group(group).id
        exp_ids: List[str] = list(
            set([self.resolve_experiment(experiment).id for experiment in experiments])
        )
        self.request(
            f"groups/{self.url_quote(group_id)}",
            method="PATCH",
            data=GroupPatch(add_experiments=exp_ids),
            exceptions_for_status={404: GroupNotFound(self._not_found_err_msg(group))},
        )

    def remove_experiments(self, group: Union[str, Group], *experiments: Union[str, Experiment]):
        """
        Remove experiments from a group.

        :param group: The group ID, name, or object.
        :param experiments: Experiments to remove from the group.

        :raises GroupNotFound: If the group can't be found.
        :raises ExperimentNotFound: If any of the given experiments don't exist.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        group_id = self.resolve_group(group).id
        exp_ids: List[str] = list(
            set([self.resolve_experiment(experiment).id for experiment in experiments])
        )
        self.request(
            f"groups/{self.url_quote(group_id)}",
            method="PATCH",
            data=GroupPatch(remove_experiments=exp_ids),
            exceptions_for_status={404: GroupNotFound(self._not_found_err_msg(group))},
        )

    def list_experiments(self, group: Union[str, Group]) -> List[Experiment]:
        """
        List experiments in a group.

        :param group: The group ID, name, or object.

        :raises GroupNotFound: If the group can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        group_id = self.resolve_group(group).id
        exp_ids = self.request(
            f"groups/{self.url_quote(group_id)}/experiments",
            method="GET",
            exceptions_for_status={404: GroupNotFound(self._not_found_err_msg(group))},
        ).json()
        # TODO: make these requests concurrently.
        return [self.beaker.experiment.get(exp_id) for exp_id in exp_ids or []]

    def export_experiments(
        self, group: Union[str, Group], quiet: bool = False
    ) -> Generator[bytes, None, None]:
        """
        Export all experiments and metrics in a group as a CSV.

        Returns a generator that should be exhausted to get the complete file.

        :param group: The group ID, name, or object.
        :param quiet: If ``True``, progress won't be displayed.

        :raises GroupNotFound: If the group can't be found.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        group_id = self.resolve_group(group).id
        resp = self.request(
            f"groups/{self.url_quote(group_id)}/export.csv",
            method="GET",
            exceptions_for_status={404: GroupNotFound(self._not_found_err_msg(group))},
            stream=True,
        ).iter_content(chunk_size=1024)

        from ..progress import get_group_experiments_progress

        with get_group_experiments_progress(quiet) as progress:
            task_id = progress.add_task("Downloading:")
            total = 0
            for chunk in resp:
                if chunk:
                    advance = len(chunk)
                    total += advance
                    progress.update(task_id, total=total + 1, advance=advance)
                    yield chunk

    def url(self, group: Union[str, Group]) -> str:
        """
        Get the URL for a group.

        :param group: The group ID, name, or object.

        :raises GroupNotFound: If the group can't be found.
        """
        group_id = self.resolve_group(group).id
        return f"{self.config.agent_address}/gr/{self.url_quote(group_id)}/compare"

    def _not_found_err_msg(self, group: Union[str, Group]) -> str:
        group = group if isinstance(group, str) else group.id
        return (
            f"'{group}': Make sure you're using a valid Beaker group ID or the "
            f"*full* name of the group (with the account prefix, e.g. 'username/group_name')"
        )
