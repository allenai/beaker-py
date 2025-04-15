from pathlib import Path

import pytest

from beaker.data_model import *
from beaker.data_model.base import MappedSequence
from beaker.exceptions import ValidationError


def test_data_source_validation():
    with pytest.raises(ValidationError, match="Exactly one"):
        DataSource()

    with pytest.raises(ValidationError, match="Exactly one"):
        DataSource(beaker="foo", host_path="bar")

    with pytest.raises(ValidationError, match="Exactly one"):
        DataSource(beaker="foo", hostPath="bar")  # type: ignore

    assert DataSource(host_path="bar").host_path == "bar"


def test_experiment_spec_from_and_to_json_and_file(beaker_cluster_name: str, tmp_path: Path):
    json_spec = {
        "version": "v2",
        "budget": "ai2/allennlp",
        "tasks": [
            {
                "name": "main",
                "image": {"docker": "hello-world"},
                "context": {"cluster": beaker_cluster_name},
                "result": {"path": "/unused"},
                "resources": {"memory": "512m", "sharedMemory": "512m"},
                "hostNetworking": False,
                "leaderSelection": False,
            },
        ],
    }

    spec = ExperimentSpec.from_json(json_spec)
    assert spec.to_json() == json_spec

    spec_path = tmp_path / "spec.yml"
    spec.to_file(spec_path)
    assert ExperimentSpec.from_file(spec_path) == spec


def test_experiment_spec_from_with_timeout(beaker_cluster_name: str):
    json_spec = {
        "version": "v2",
        "budget": "ai2/allennlp",
        "tasks": [
            {
                "name": "main",
                "image": {"docker": "hello-world"},
                "context": {"cluster": beaker_cluster_name},
                "result": {"path": "/unused"},
                "resources": {"memory": "512m", "sharedMemory": "512m"},
                "hostNetworking": False,
                "leaderSelection": False,
                "timeout": "10m",
            },
        ],
    }

    spec = ExperimentSpec.from_json(json_spec)
    assert spec.tasks[0].timeout == 600000000000

    json_spec = {
        "version": "v2",
        "budget": "ai2/allennlp",
        "tasks": [
            {
                "name": "main",
                "image": {"docker": "hello-world"},
                "context": {"cluster": beaker_cluster_name},
                "result": {"path": "/unused"},
                "resources": {"memory": "512m", "sharedMemory": "512m"},
                "hostNetworking": False,
                "leaderSelection": False,
                "timeout": None,
            },
        ],
    }

    spec = ExperimentSpec.from_json(json_spec)
    assert spec.tasks[0].timeout is None

    json_spec = {
        "version": "v2",
        "budget": "ai2/allennlp",
        "tasks": [
            {
                "name": "main",
                "image": {"docker": "hello-world"},
                "context": {"cluster": beaker_cluster_name},
                "result": {"path": "/unused"},
                "resources": {"memory": "512m", "sharedMemory": "512m"},
                "hostNetworking": False,
                "leaderSelection": False,
                "timeout": 600000000000.0,
            },
        ],
    }

    spec = ExperimentSpec.from_json(json_spec)
    assert isinstance(spec.tasks[0].timeout, int)
    assert spec.tasks[0].timeout == 600000000000


def test_experiment_spec_validation():
    with pytest.raises(ValidationError, match="Duplicate task name"):
        ExperimentSpec.from_json(
            {
                "budget": "ai2/allennlp",
                "tasks": [
                    {
                        "name": "main",
                        "image": {"docker": "hello-world"},
                        "context": {"cluster": "foo"},
                        "result": {"path": "/unused"},
                    },
                    {
                        "name": "main",
                        "image": {"docker": "hello-world"},
                        "context": {"cluster": "bar"},
                        "result": {"path": "/unused"},
                    },
                ],
            }
        )
    with pytest.raises(ValidationError, match="Duplicate task name"):
        ExperimentSpec(
            budget="ai2/allennlp",
            tasks=[
                TaskSpec(
                    name="main",
                    image={"docker": "hello-world"},  # type: ignore
                    context={"cluster": "foo"},  # type: ignore
                    result={"path": "/unused"},  # type: ignore
                ),
                TaskSpec(
                    name="main",
                    image={"docker": "hello-world"},  # type: ignore
                    context={"cluster": "bar"},  # type: ignore
                    result={"path": "/unused"},  # type: ignore
                ),
            ],
        )
    spec = ExperimentSpec(budget="ai2/allennlp").with_task(
        TaskSpec.new("main", "foo", docker_image="hello-world")
    )
    with pytest.raises(ValueError, match="A task with the name"):
        spec.with_task(TaskSpec.new("main", "bar", docker_image="hello-world"))


def test_snake_case_vs_lower_camel_case():
    for x in (DataSource(host_path="/tmp/foo"), DataSource(hostPath="/tmp/foo")):  # type: ignore
        assert (
            str(x)
            == "DataSource(beaker=None, host_path='/tmp/foo', weka=None, result=None, secret=None)"
        )
        assert x.host_path == "/tmp/foo"
        x.host_path = "/tmp/bar"
        assert (
            str(x)
            == "DataSource(beaker=None, host_path='/tmp/bar', weka=None, result=None, secret=None)"
        )
        assert x.to_json() == {"hostPath": "/tmp/bar"}


def test_digest_init():
    # All of these are equivalent:
    for digest in (
        # String form.
        Digest("SHA256 iA02Sx8UNLYvMi49fDwdGjyy5ssU+ttuN1L4L3/JvZA="),
        # Hex-encoded string.
        Digest(
            "880d364b1f1434b62f322e3d7c3c1d1a3cb2e6cb14fadb6e3752f82f7fc9bd90", algorithm="SHA256"
        ),
        # Raw bytes.
        Digest(
            b"\x88\r6K\x1f\x144\xb6/2.=|<\x1d\x1a<\xb2\xe6\xcb\x14\xfa\xdbn7R\xf8/\x7f\xc9\xbd\x90",
            algorithm="SHA256",
        ),
    ):
        assert digest.value == "880d364b1f1434b62f322e3d7c3c1d1a3cb2e6cb14fadb6e3752f82f7fc9bd90"


def test_digest_hashable():
    digest = Digest.from_encoded("SHA256 0Q/XIPetp+QFDce6EIYNVcNTCZSlPqmEfVs1eFEMK0Y=")
    d = {digest: 1}
    assert digest in d


def test_mapped_sequence():
    ms = MappedSequence([1, 2, 3], {"a": 1, "b": 2, "c": 3})
    assert ms["a"] == 1
    assert ms[0] == 1
    assert len(ms) == 3
    assert "a" in ms
    assert 1 in ms
    assert list(ms) == [1, 2, 3]
    assert set(ms.keys()) == {"a", "b", "c"}
    assert ms.get("a") == 1
    assert "z" not in ms


@pytest.mark.parametrize(
    "cluster", [["ai2/jupiter-cirrascale-2", "ai2/saturn-cirrascale"], "ai2/jupiter-cirrascale-2"]
)
def test_experiment_spec_new_with_cluster(cluster):
    spec = ExperimentSpec.new("ai2/allennlp", cluster=cluster)
    assert spec.tasks[0].context.cluster is None
    assert spec.tasks[0].constraints is not None
    assert isinstance(spec.tasks[0].constraints.cluster, list)


def test_task_spec_with_constraint():
    task_spec = TaskSpec.new("main", constraints=Constraints(cluster=["ai2/saturn-cirrascale"]))
    new_task_spec = task_spec.with_constraint(cluster=["ai2/jupiter-cirrascale-2"])
    assert new_task_spec.constraints is not None
    assert new_task_spec.constraints.cluster == ["ai2/jupiter-cirrascale-2"]
    # Shouldn't modify the original.
    assert task_spec.constraints is not None
    assert task_spec.constraints.cluster == ["ai2/saturn-cirrascale"]

    # These methods should all be equivalent.
    for task_spec in (
        TaskSpec.new("main", constraints={"cluster": ["ai2/general-cirrascale"]}),
        TaskSpec.new("main", cluster="ai2/general-cirrascale"),
        TaskSpec.new("main", cluster=["ai2/general-cirrascale"]),
    ):
        assert task_spec.constraints is not None
        assert task_spec.constraints.cluster == ["ai2/general-cirrascale"]


def test_constraints_behave_like_dictionaries():
    c = Constraints()
    c["cluster"] = ["ai2/general-cirrascale"]
    assert c.cluster == ["ai2/general-cirrascale"]


def test_constraints_extra_fields():
    c = Constraints(cluster=["ai2/general-cirrascale"], gpus=["A100"])  # type: ignore
    assert hasattr(c, "gpus")


def test_job_status_with_canceled_code():
    from datetime import datetime

    status = JobStatus(created=datetime.utcnow(), canceled_code=0)
    assert status.canceled_code == CanceledCode.not_set

    status = JobStatus(created=datetime.utcnow(), canceled_code=6)
    assert status.canceled_code == 6
