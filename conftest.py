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
    return petname.generate() + "-" + str(uuid.uuid4())[:8]


def beaker_object_fixture(client: Beaker, service: str):
    name = unique_name()
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
    name = "ai2/petew-testing"
    return name


@pytest.fixture()
def alternate_workspace_name() -> str:
    name = "ai2/petew-testing-alternate"
    return name


@pytest.fixture()
def client(workspace_name):
    beaker_client = Beaker.from_env(default_workspace=workspace_name, default_org="ai2")
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
def alternate_beaker_image_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "image")


@pytest.fixture()
def beaker_cluster_name() -> str:
    cluster = "ai2/petew-cpu"
    return cluster


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
    return "hello-world"


@pytest.fixture()
def hello_world_experiment_id() -> str:
    return "01FPB5WGRTM33P5AE6A28MT8QF"


@pytest.fixture()
def hello_world_image_name() -> str:
    return "petew/hello-world"


@pytest.fixture()
def hello_world_job_id() -> str:
    return "01G0062R1K182CGR5559GHT5ED"


@pytest.fixture()
def beaker_node_id() -> str:
    return "01FXTYPFQ1QQ7XV4SH8VTCRZMG"


@pytest.fixture()
def secret_name(client: Beaker) -> Generator[str, None, None]:
    yield from beaker_object_fixture(client, "secret")


@pytest.fixture()
def archived_workspace_name() -> str:
    return "ai2/petew-testing-archived"


@pytest.fixture()
def archived_workspace(client: Beaker, archived_workspace_name: str) -> Workspace:
    workspace = client.workspace.ensure(archived_workspace_name)
    if not workspace.archived:
        return client.workspace.archive(archived_workspace_name)
    else:
        return workspace


@pytest.fixture()
def squad_dataset_name(client: Beaker) -> str:
    return "petew/squad-train"


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
    return "ex_1l1an142rn9l"


@pytest.fixture()
def experiment_id_with_results() -> str:
    return "ex_1l1an142rn9l"
