from typing import TYPE_CHECKING, Dict, Optional, Union

from ..data_model import *
from ..exceptions import *
from .service_client import ServiceClient

if TYPE_CHECKING:
    from rich.progress import TaskID


class ImageClient(ServiceClient):
    """
    Accessed via :data:`Beaker.image <beaker.Beaker.image>`.
    """

    def get(self, image: str) -> Image:
        """
        Get info about an image on Beaker.

        :param image: The Beaker image ID or name.

        :raises ImageNotFound: If the image can't be found on Beaker.
        :raises HTTPError: Any other HTTP exception that can occur.
        """

        def _get(id: str) -> Image:
            return Image.from_json(
                self.request(
                    f"images/{self.url_quote(id)}",
                    exceptions_for_status={404: ImageNotFound(self._not_found_err_msg(id))},
                ).json()
            )

        try:
            # Could be an ID or full name, so we try that first.
            return _get(image)
        except ImageNotFound:
            if "/" not in image:
                # Now try with adding the account name.
                try:
                    return _get(f"{self.beaker.account.name}/{image}")
                except ImageNotFound:
                    pass
            raise

    def create(
        self,
        name: str,
        image_tag: str,
        workspace: Optional[str] = None,
        quiet: bool = False,
        commit: bool = True,
    ) -> Image:
        """
        Upload a Docker image to Beaker.

        :param name: The name to assign to the image on Beaker.
        :param image_tag: The tag of the local image you're uploading.
        :param workspace: The workspace to upload the image to. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param quiet: If ``True``, progress won't be displayed.
        :param commit: Whether to commit the image after successful upload.

        :raises ValueError: If the image name is invalid.
        :raises ImageConflict: If an image with the given name already exists.
        :raises WorkspaceNotSet: If neither ``workspace`` nor
            :data:`Beaker.config.defeault_workspace <beaker.Config.default_workspace>` are set.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.

        """
        self.validate_beaker_name(name)
        workspace: Workspace = self.resolve_workspace(workspace)

        # Get local Docker image object.
        image = self.docker.images.get(image_tag)

        # Create new image on Beaker.
        image_id = self.request(
            "images",
            method="POST",
            data={"Workspace": workspace.id, "ImageID": image.id, "ImageTag": image_tag},
            query={"name": name},
            exceptions_for_status={409: ImageConflict(name)},
        ).json()["id"]

        # Get the repo data for the Beaker image.
        repo = ImageRepo.from_json(
            self.request(f"images/{image_id}/repository", query={"upload": True}).json()
        )

        # Tag the local image with the new tag for the Beaker image.
        image.tag(repo.image_tag)

        # Push the image to Beaker.
        from ..progress import get_image_upload_progress

        with get_image_upload_progress(quiet) as progress:
            layer_id_to_task: Dict[str, "TaskID"] = {}
            for layer_state_data in self.docker.api.push(
                repo.image_tag,
                stream=True,
                decode=True,
                auth_config={
                    "username": repo.auth.user,
                    "password": repo.auth.password,
                    "server_address": repo.auth.server_address,
                },
            ):
                if "id" not in layer_state_data or "status" not in layer_state_data:
                    continue

                layer_state = DockerLayerUploadState.from_json(layer_state_data)

                # Get progress task ID for layer, initializing if it doesn't already exist.
                task_id: "TaskID"
                if layer_state.id not in layer_id_to_task:
                    task_id = progress.add_task(layer_state.id, start=True, total=1)
                    layer_id_to_task[layer_state.id] = task_id
                else:
                    task_id = layer_id_to_task[layer_state.id]

                if layer_state.status in {
                    DockerLayerUploadStatus.preparing,
                    DockerLayerUploadStatus.waiting,
                }:
                    progress.update(
                        task_id,
                        total=1,
                        completed=0,
                        description=f"{layer_state.id}: {layer_state.status.title()}",
                    )
                elif layer_state.status == DockerLayerUploadStatus.pushing:
                    progress.update(
                        task_id,
                        description=f"{layer_state.id}: Pushing",
                    )
                    if layer_state.progress_detail.total and layer_state.progress_detail.current:
                        progress.update(
                            task_id,
                            total=layer_state.progress_detail.total,
                            completed=layer_state.progress_detail.current,
                        )
                elif layer_state.status == DockerLayerUploadStatus.pushed:
                    progress.update(
                        task_id,
                        total=1,
                        completed=1,
                        description=f"{layer_state.id}: Push complete",
                    )
                elif layer_state.status == "layer already exists":
                    progress.update(
                        task_id,
                        total=1,
                        completed=1,
                        description=f"{layer_state.id}: Already exists",
                    )
                else:
                    raise ValueError(f"unhandled status '{layer_state.status}' (layer_state)")

        if commit:
            return self.commit(image_id)
        else:
            return self.get(image_id)

    def commit(self, image: Union[str, Image]) -> Image:
        """
        Commit an image.

        :param image: The Beaker image ID, name, or object.

        :raises ImageNotFound: If the image can't be found on Beaker.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        image_id = self.resolve_image(image).id
        return Image.from_json(
            self.request(f"images/{image_id}", method="PATCH", data={"Commit": True}).json()
        )

    def delete(self, image: Union[str, Image]):
        """
        Delete an image on Beaker.

        :param image: The Beaker image ID, name, or object.

        :raises ImageNotFound: If the image can't be found on Beaker.
        :raises BeakerError: Any other :class:`~beaker.exceptions.BeakerError` type that can occur.
        :raises HTTPError: Any other HTTP exception that can occur.
        """
        image_id = self.resolve_image(image).id
        self.request(
            f"images/{self.url_quote(image_id)}",
            method="DELETE",
            exceptions_for_status={404: ImageNotFound(self._not_found_err_msg(image_id))},
        )

    def _not_found_err_msg(self, image: str) -> str:
        return (
            f"'{image}': Make sure you're using a valid Beaker image ID or the "
            f"*full* name of the image (with the account prefix, e.g. 'username/image_name')"
        )
