import sys

from beaker import Beaker, ImageNotFound


def main(
    experiment: str = "hello-world",
    image: str = "hello-world",
    cluster: str = "AI2/petew-cpu",
    org: str = "AI2",
):
    # Setup.
    beaker = Beaker.from_env()
    beaker.config.default_workspace = f"{org}/{beaker.user}"

    # Check if image exists on Beaker and create it if it doesn't.
    beaker_image = image.replace(":", "-")
    try:
        image_data = beaker.get_image(f"{beaker.user}/{beaker_image}")
    except ImageNotFound:
        image_data = beaker.create_image(
            name=beaker_image,
            image_tag=image,
        )

    # Submit experiment.
    experiment_data = beaker.create_experiment(
        experiment,
        {
            "version": "v2-alpha",
            "tasks": [
                {
                    "name": "main",
                    "image": {"beaker": image_data["id"]},
                    "context": {"cluster": cluster},
                    "result": {"path": "/unused"},  # required even if the task produces no output.
                },
            ],
        },
    )
    experiment_id = experiment_data["id"]
    print(
        f"Experiment {experiment_id} submitted.\n"
        f"See progress at https://beaker.org/ex/{experiment_id}"
    )


if __name__ == "__main__":
    main(*sys.argv[1:])
