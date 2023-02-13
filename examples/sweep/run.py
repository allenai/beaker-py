"""
This script will upload an image to Beaker and then submit a bunch
of experiments with different inputs. It will wait for all experiments to finish
and then collect the results.

See the output of 'python run.py --help' for usage.
"""

import argparse
import uuid

import petname
from rich import print, progress, table, traceback

from beaker import *


def unique_name() -> str:
    """Helper function to generate a unique name for the image, group, and each experiment."""
    return petname.generate() + "-" + str(uuid.uuid4())[:8]  # type: ignore


def main(image: str, workspace: str):
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

        # Launch experiments.
        experiments = []
        for x in progress.track(range(5), description="Launching experiments..."):
            spec = ExperimentSpec.new(
                description=f"Run {x+1} of sweep {sweep_name}",
                beaker_image=beaker_image.full_name,
                result_path="/output",
                priority=Priority.preemptible,
                arguments=[str(x)],
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
    opts = parser.parse_args()

    main(image=opts.image, workspace=opts.workspace)
