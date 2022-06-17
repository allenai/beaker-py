import pytest


@pytest.fixture(autouse=True)
def doctest_fixtures(
    doctest_namespace,
    client,
    workspace_name,
    docker_image_name,
    beaker_image_name,
    beaker_cluster_name,
    beaker_cloud_cluster_name,
    beaker_on_prem_cluster_name,
    experiment_name,
    dataset_name,
    download_path,
    beaker_org_name,
    beaker_node_id,
    secret_name,
    group_name,
    hello_world_experiment_name,
):
    doctest_namespace["beaker"] = client
    doctest_namespace["workspace_name"] = workspace_name
    doctest_namespace["docker_image_name"] = docker_image_name
    doctest_namespace["beaker_image_name"] = beaker_image_name
    doctest_namespace["beaker_cluster_name"] = beaker_cluster_name
    doctest_namespace["beaker_cloud_cluster_name"] = beaker_cloud_cluster_name
    doctest_namespace["beaker_on_prem_cluster_name"] = beaker_on_prem_cluster_name
    doctest_namespace["experiment_name"] = experiment_name
    doctest_namespace["dataset_name"] = dataset_name
    doctest_namespace["download_path"] = download_path
    doctest_namespace["beaker_org_name"] = beaker_org_name
    doctest_namespace["beaker_node_id"] = beaker_node_id
    doctest_namespace["secret_name"] = secret_name
    doctest_namespace["group_name"] = group_name
    doctest_namespace["hello_world_experiment_name"] = hello_world_experiment_name
