import argparse
import uuid

import petname
from rich import print, progress, table, traceback

from beaker import *


def unique_name() -> str:
    return petname.generate() + "-" + str(uuid.uuid4())[:8]  # type: ignore


def main(image: str, workspace: str, cluster: str):
    beaker = Beaker.from_env(default_workspace=workspace)
    sweep_name = unique_name()
    print(f"Starting sweep '{sweep_name}'...\n")

    # Using the `beaker.session()` context manager is not necessary, but it does
    # speed things up since it allows the Beaker client to reuse the same TCP connection
    # for all requests made within-context.
    with beaker.session():
        # Upload image to Beaker.
        print(f"Uploading image '{image}' to Beaker...")
        beaker_image = beaker.image.create(unique_name(), image)
        print(
            f"Image uploaded as '{beaker_image.full_name}', view at {beaker.image.url(beaker_image)}\n"
        )
        base_spec = ExperimentSpec()
        base_task = TaskSpec.new(
            "main", cluster, beaker_image=beaker_image.full_name, result_path="/output"
        )

        # Launch experiments.
        experiments = []
        for x in progress.track(range(5), description="Launching experiments..."):
            spec = base_spec.with_description(f"Run {x+1} of sweep {sweep_name}").with_task(
                base_task.with_arguments([str(x)])
            )
            experiment = beaker.experiment.create(f"{sweep_name}-{x+1}", spec)
            experiments.append(experiment)
        print()

        # Create group.
        print("Creating group for sweep...")
        group = beaker.group.create(
            sweep_name, *experiments, description="Group for sweep {sweep_name}"
        )
        print(f"Group '{group.full_name}' created, view at {beaker.group.url(group)}\n")

        # Wait for experiments to finish.
        print("Waiting for experiments to finalize...\n")
        experiments = beaker.experiment.wait_for(*experiments)
        print()

        # Display results as a table.
        results_table = table.Table(title="Results for sweep")
        results_table.add_column("Input")
        results_table.add_column("Output")
        for x, experiment in enumerate(
            progress.track(experiments, description="Gathering results...")
        ):
            metrics = beaker.experiment.metrics(experiment)
            assert metrics is not None
            results_table.add_row(f"x = {x}", f"{metrics['result']:.4f}")
        print()
        print(results_table)


if __name__ == "__main__":
    traceback.install()

    parser = argparse.ArgumentParser(description="Run a hyperparameter sweep in Beaker")
    parser.add_argument(
        "image", type=str, help="""The tag of the local Docker image built from the Dockerfile."""
    )
    parser.add_argument("workspace", type=str, help="""The Beaker workspace to use.""")
    parser.add_argument("cluster", type=str, help="""The cluster to use.""")
    opts = parser.parse_args()

    main(image=opts.image, workspace=opts.workspace, cluster=opts.cluster)
