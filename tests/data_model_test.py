import pytest

from beaker.data_model import *
from beaker.exceptions import ValidationError


def test_image_source_validation():
    with pytest.raises(ValidationError, match="'beaker' or 'docker'"):
        ImageSource()

    with pytest.raises(ValidationError, match="'beaker' or 'docker'"):
        ImageSource(beaker="foo", docker="bar")

    ImageSource(beaker="foo")


def test_data_source_validation():
    with pytest.raises(ValidationError, match="Exactly one"):
        DataSource()

    with pytest.raises(ValidationError, match="Exactly one"):
        DataSource(beaker="foo", host_path="bar")

    with pytest.raises(ValidationError, match="Exactly one"):
        DataSource(beaker="foo", hostPath="bar")

    assert DataSource(host_path="bar").host_path == "bar"


def test_experiment_spec_from_and_to_json(beaker_cluster_name):
    json_spec = {
        "version": "v2-alpha",
        "tasks": [
            {
                "name": "main",
                "image": {"docker": "hello-world"},
                "context": {"cluster": beaker_cluster_name},
                "result": {"path": "/unused"},
                "resources": {"memory": "512m", "sharedMemory": "512m"},
            },
        ],
    }
    spec = ExperimentSpec.from_json(json_spec)
    assert spec.to_json() == json_spec
