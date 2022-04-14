from typing import Dict, Optional, Union

from rich.progress import BarColumn, Progress, TaskID, TimeRemainingColumn

from ..data_model import *
from ..exceptions import *
from ..util import DownloadUploadColumn
from .service_client import ServiceClient


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
    ) -> Image:
        """
        Upload a Docker image to Beaker.

        :param name: The name to assign to the image on Beaker.
        :param image_tag: The tag of the local image you're uploading.
        :param workspace: The workspace to upload the image to. If not specified,
            :data:`Beaker.config.default_workspace <beaker.Config.default_workspace>` is used.
        :param quiet: If ``True``, progress won't be displayed.

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
        image_data = self.request(
            "images",
            method="POST",
            data={"Workspace": workspace.id, "ImageID": image.id, "ImageTag": image_tag},
            query={"name": name},
            exceptions_for_status={409: ImageConflict(name)},
        ).json()

        # Get the repo data for the Beaker image.
        repo_data = self.request(
            f"images/{image_data['id']}/repository", query={"upload": True}
        ).json()
        auth = repo_data["auth"]

        # Tag the local image with the new tag for the Beaker image.
        image.tag(repo_data["imageTag"])

        # Push the image to Beaker.
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
            DownloadUploadColumn(),
            disable=quiet,
        ) as progress:
            layer_id_to_task: Dict[str, TaskID] = {}
            for line in self.docker.api.push(
                repo_data["imageTag"],
                stream=True,
                decode=True,
                auth_config={
                    "username": auth["user"],
                    "password": auth["password"],
                    "server_address": auth["server_address"],
                },
            ):
                if "id" not in line or "status" not in line:
                    continue
                layer_id = line["id"]
                status = line["status"].lower()
                progress_detail = line.get("progressDetail")
                task_id: TaskID
                if layer_id not in layer_id_to_task:
                    task_id = progress.add_task(layer_id, start=True, total=1)
                    layer_id_to_task[layer_id] = task_id
                else:
                    task_id = layer_id_to_task[layer_id]
                if status in {"preparing", "waiting"}:
                    progress.update(
                        task_id, total=1, completed=0, description=f"{layer_id}: {status.title()}"
                    )
                elif status == "pushing" and progress_detail:
                    progress.update(
                        task_id,
                        total=progress_detail["total"],
                        completed=progress_detail["current"],
                        description=f"{layer_id}: Pushing",
                    )
                elif status == "pushed":
                    progress.update(
                        task_id, total=1, completed=1, description=f"{layer_id}: Push complete"
                    )
                elif status == "layer already exists":
                    progress.update(
                        task_id, total=1, completed=1, description=f"{layer_id}: Already exists"
                    )
                else:
                    raise ValueError(f"unhandled status '{status}' ({line})")

        # Commit changes to Beaker.
        self.request(f"images/{image_data['id']}", method="PATCH", data={"Commit": True})

        # Return info about the Beaker image.
        return self.get(image_data["id"])

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
