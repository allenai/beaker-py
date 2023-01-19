from pathlib import Path

import pytest

from beaker.data_model import *
from beaker.exceptions import ValidationError


def test_data_source_validation():
    with pytest.raises(ValidationError, match="Exactly one"):
        DataSource()

    with pytest.raises(ValidationError, match="Exactly one"):
        DataSource(beaker="foo", host_path="bar")

    with pytest.raises(ValidationError, match="Exactly one"):
        DataSource(beaker="foo", hostPath="bar")  # type: ignore

    assert DataSource(host_path="bar").host_path == "bar"


def test_experiment_spec_from_and_to_json_and_file(beaker_cloud_cluster_name: str, tmp_path: Path):
    json_spec = {
        "version": "v2",
        "tasks": [
            {
                "name": "main",
                "image": {"docker": "hello-world"},
                "context": {"cluster": beaker_cloud_cluster_name},
                "result": {"path": "/unused"},
                "resources": {"memory": "512m", "sharedMemory": "512m"},
            },
        ],
    }

    spec = ExperimentSpec.from_json(json_spec)
    assert spec.to_json() == json_spec

    spec_path = tmp_path / "spec.yml"
    spec.to_file(spec_path)
    assert ExperimentSpec.from_file(spec_path) == spec


def test_experiment_spec_validation():
    with pytest.raises(ValidationError, match="Duplicate task name"):
        ExperimentSpec.from_json(
            {
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
                ]
            }
        )
    with pytest.raises(ValidationError, match="Duplicate task name"):
        ExperimentSpec(
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
            ]
        )
    spec = ExperimentSpec().with_task(TaskSpec.new("main", "foo", docker_image="hello-world"))
    with pytest.raises(ValueError, match="A task with the name"):
        spec.with_task(TaskSpec.new("main", "bar", docker_image="hello-world"))


def test_snake_case_vs_lower_camel_case():
    for x in (DataSource(host_path="/tmp/foo"), DataSource(hostPath="/tmp/foo")):  # type: ignore
        assert str(x) == "DataSource(beaker=None, host_path='/tmp/foo', result=None, secret=None)"
        assert x.host_path == "/tmp/foo"
        x.host_path = "/tmp/bar"
        assert str(x) == "DataSource(beaker=None, host_path='/tmp/bar', result=None, secret=None)"
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
