"""
This is the script that will run on Beaker as the Docker image's "entrypoint".

All it does is write out a simple JSON file with a random number in it to
the experiment's result directory. This is just meant to simulate the results
of a training/evaluation pipeline.
"""

import json
import random
import sys

# NOTE: it's important that this file is called 'metrics.json'. That tells Beaker
# to collect metrics for the task from this file.
OUTPUT_PATH = "/output/metrics.json"


def main(x: int):
    random.seed(x)
    with open(OUTPUT_PATH, "w") as out_file:
        json.dump({"result": random.random()}, out_file)


if __name__ == "__main__":
    main(int(sys.argv[1]))
