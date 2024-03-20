import logging
import uuid
from pathlib import Path
from typing import Generator

import petname
import pytest

from beaker import exceptions
from beaker.client import Beaker
from beaker.data_model import *

logger = logging.getLogger(__name__)


def unique_name() -> str:
    return petname.generate() + "-" + str(uuid.uuid4())[:8]  # type: ignore


def beaker_object_fixture(client: Beaker, service: str, prefix: str = ""):
    name = prefix + unique_name()
    service_client = getattr(client, service)
    not_found_exception = getattr(exceptions, f"{service.title()}NotFound")
    yield name
    try:
        logger.info("Attempting to remove %s '%s' from Beaker", service, name)
        service_client.delete(name)
        logger.info("Successfully deleted %s '%s' from Beaker", service, name)
    except not_found_exception:
        logger.info("%s '%s' not found on Beaker", service.title(), name)


@pytest.fixture()
def workspace_name() -> str:
    name = "ai2/beaker-py-testing"
    return name


@pytest.fixture()
def alternate_workspace_name() -> str:
    name = "ai2/beaker-py-testing-alternative"
    return name


@pytest.fixture()
def client(workspace_name):
    beaker_client = Beaker.from_env(
        session=True, default_workspace=workspace_name, default_org="ai2"
    )
    return beaker_client


@pytest.fixture()
def alternate_workspace(client: Beaker, alternate_workspace_name: str) -> Workspace:
    return client.workspace.get(alternate_workspace_name)


@pytest.fixture
def beaker_org_name() -> str:
    return "ai2"


@pytest.fixture()
def beaker_org(client: Beaker, beaker_org_name: str) -> Organization:
    return client.organization.get(beaker_org_name)


@pytest.fixture()
def docker_image_name(client: Beaker):
    image = "hello-world"
    client.docker.images.pull(image)
    return image


@pytest.fixture()
def beaker_image_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "image")


@pytest.fixture()
def beaker_python_image_name() -> str:
    return "petew/python-3-10-alpine"


@pytest.fixture()
def alternate_beaker_image_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "image")


@pytest.fixture()
def beaker_cluster_name() -> str:
    return "ai2/canary"


@pytest.fixture()
def beaker_on_prem_cluster_name() -> str:
    return "ai2/allennlp-cirrascale"


@pytest.fixture()
def experiment_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "experiment")


@pytest.fixture()
def alternate_experiment_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "experiment")


@pytest.fixture()
def dataset_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "dataset")


@pytest.fixture()
def alternate_dataset_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "dataset")


@pytest.fixture()
def download_path(dataset_name, tmp_path) -> Path:
    path = tmp_path / dataset_name
    return path


@pytest.fixture()
def hello_world_experiment_name() -> str:
    return "hello-world-1"


@pytest.fixture()
def hello_world_experiment_id() -> str:
    return "01GRYY998GG0VP97MKRE574GKA"


@pytest.fixture()
def hello_world_image_name() -> str:
    return "petew/hello-world"


@pytest.fixture()
def hello_world_job_id() -> str:
    return "01GRYY9P9G5ZJ0F66NV3AHN9AN"


@pytest.fixture()
def beaker_node_id(client: Beaker, beaker_on_prem_cluster_name: str) -> str:
    return client.cluster.nodes(beaker_on_prem_cluster_name)[0].id


@pytest.fixture()
def secret_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "secret")


@pytest.fixture()
def archived_workspace_name() -> str:
    return "ai2/beaker-py-testing-archived"


@pytest.fixture()
def archived_workspace(client: Beaker, archived_workspace_name: str) -> Workspace:
    workspace = client.workspace.ensure(archived_workspace_name)
    if not workspace.archived:
        return client.workspace.archive(archived_workspace_name)
    else:
        return workspace


@pytest.fixture()
def squad_dataset_file_name() -> str:
    return "squad-train.arrow"


@pytest.fixture()
def squad_dataset_name(client: Beaker, squad_dataset_file_name) -> Generator[str, None, None]:
    for dataset_name in beaker_object_fixture(client, "dataset", prefix="squad"):
        dataset = client.dataset.create(dataset_name, commit=False)
        client.dataset.upload(dataset, b"blahblahblah", squad_dataset_file_name)
        client.dataset.commit(dataset)
        yield dataset_name


@pytest.fixture()
def alternate_user(client: Beaker) -> Account:
    return client.account.get("epwalsh10")


@pytest.fixture()
def group_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "group")


@pytest.fixture()
def alternate_group_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "group")


@pytest.fixture()
def experiment_id_with_metrics() -> str:
    return "01G371J03VGJGK720TMZWFQNV3"


# experiment was deleted
#  @pytest.fixture()
#  def experiment_id_with_results() -> str:
#      return "01G371J03VGJGK720TMZWFQNV3"
