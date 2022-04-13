import uuid
from pathlib import Path
from typing import Generator

import petname
import pytest

from beaker.client import Beaker
from beaker.data_model import *
from beaker.exceptions import *


@pytest.fixture()
def workspace_name() -> str:
    workspace = "ai2/petew-testing"
    return workspace


@pytest.fixture()
def client(workspace_name):
    beaker_client = Beaker.from_env(default_workspace=workspace_name, default_org="ai2")
    return beaker_client


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
    image = petname.generate() + "-" + str(uuid.uuid4())[:8]
    yield image
    try:
        client.image.delete(f"{client.account.whoami().name}/{image}")
    except ImageNotFound:
        pass


@pytest.fixture()
def beaker_cluster_name() -> str:
    cluster = "ai2/petew-cpu"
    return cluster


@pytest.fixture()
def beaker_on_prem_cluster_name() -> str:
    return "ai2/allennlp-cirrascale"


@pytest.fixture()
def experiment_name(client: Beaker) -> Generator[str, None, None]:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    yield name
    try:
        client.experiment.delete(f"{client.account.whoami().name}/{name}")
    except ExperimentNotFound:
        pass


@pytest.fixture()
def alternate_experiment_name(client: Beaker) -> Generator[str, None, None]:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    yield name
    try:
        client.experiment.delete(f"{client.account.whoami().name}/{name}")
    except ExperimentNotFound:
        pass


@pytest.fixture()
def dataset_name(client: Beaker) -> Generator[str, None, None]:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    yield name
    try:
        client.dataset.delete(f"{client.account.whoami().name}/{name}")
    except DatasetNotFound:
        pass


@pytest.fixture()
def alternate_dataset_name(client: Beaker) -> Generator[str, None, None]:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    yield name
    try:
        client.dataset.delete(f"{client.account.whoami().name}/{name}")
    except DatasetNotFound:
        pass


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
    return "hello-world"


@pytest.fixture()
def hello_world_job_id() -> str:
    return "01G0062R1K182CGR5559GHT5ED"


@pytest.fixture()
def beaker_node_id() -> str:
    return "01FXTYPFQ1QQ7XV4SH8VTCRZMG"


@pytest.fixture()
def secret_name(client: Beaker) -> Generator[str, None, None]:
    name = petname.generate() + "-" + str(uuid.uuid4())[:8]
    yield name
    try:
        client.secret.delete(name)
    except SecretNotFound:
        pass


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
