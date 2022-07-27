from beaker import Beaker, CurrentJobStatus, JobKind


def test_job_get(client: Beaker, hello_world_job_id: str):
    job = client.job.get(hello_world_job_id)
    assert job.id == hello_world_job_id
    assert job.status.current == CurrentJobStatus.finalized
    assert job.kind == JobKind.execution
    assert job.to_json()["kind"] == "execution"


def test_job_results(client: Beaker, hello_world_job_id: str):
    results = client.job.results(hello_world_job_id)
    assert results is not None


def test_job_logs(client: Beaker, hello_world_job_id: str):
    logs = "\n".join(
        [
            line.strip()
            for line in b"".join(list(client.job.logs(hello_world_job_id, quiet=True)))
            .decode()
            .split("\n")
        ]
    )
    assert (
        logs
        == """2021-12-07T19:30:24.637600011Z
2021-12-07T19:30:24.637630562Z Hello from Docker!
2021-12-07T19:30:24.637641763Z This message shows that your installation appears to be working correctly.
2021-12-07T19:30:24.637645556Z
2021-12-07T19:30:24.637648666Z To generate this message, Docker took the following steps:
2021-12-07T19:30:24.637652988Z  1. The Docker client contacted the Docker daemon.
2021-12-07T19:30:24.637656645Z  2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
2021-12-07T19:30:24.637659564Z     (amd64)
2021-12-07T19:30:24.637662606Z  3. The Docker daemon created a new container from that image which runs the
2021-12-07T19:30:24.637665558Z     executable that produces the output you are currently reading.
2021-12-07T19:30:24.637669039Z  4. The Docker daemon streamed that output to the Docker client, which sent it
2021-12-07T19:30:24.637673738Z     to your terminal.
2021-12-07T19:30:24.637676374Z
2021-12-07T19:30:24.637679313Z To try something more ambitious, you can run an Ubuntu container with:
2021-12-07T19:30:24.637682338Z  $ docker run -it ubuntu bash
2021-12-07T19:30:24.637685428Z
2021-12-07T19:30:24.637688089Z Share images, automate workflows, and more with a free Docker ID:
2021-12-07T19:30:24.637691017Z  https://hub.docker.com/
2021-12-07T19:30:24.637693808Z
2021-12-07T19:30:24.637696627Z For more examples and ideas, visit:
2021-12-07T19:30:24.637699976Z  https://docs.docker.com/get-started/
2021-12-07T19:30:24.637702728Z\n"""
    )


def test_job_logs_since(client: Beaker, hello_world_job_id: str):
    logs = "\n".join(
        [
            line.strip()
            for line in b"".join(
                list(
                    client.job.logs(
                        hello_world_job_id, quiet=True, since="2021-12-07T19:30:24.637688089Z"
                    )
                )
            )
            .decode()
            .split("\n")
        ]
    )
    assert (
        logs
        == """2021-12-07T19:30:24.637688089Z Share images, automate workflows, and more with a free Docker ID:
2021-12-07T19:30:24.637691017Z  https://hub.docker.com/
2021-12-07T19:30:24.637693808Z
2021-12-07T19:30:24.637696627Z For more examples and ideas, visit:
2021-12-07T19:30:24.637699976Z  https://docs.docker.com/get-started/
2021-12-07T19:30:24.637702728Z"""
    )
