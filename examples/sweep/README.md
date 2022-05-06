<!-- start overview -->

## Hyperparameter sweeps

This example shows how you can run a hyperparameter sweep in Beaker using **beaker-py**.

<!-- end overview -->

<!-- start run it -->

To run it, first build the Docker image:

```bash
image=sweep
docker build -t $image .
```

Then launch the sweep with:

```bash
workspace=ai2/my-sweep  # change this to the workspace of your choosing
cluster=ai2/petew-cpu  # change this to the cluster of your choosing
python run.py $image $workspace $cluster
```

<!-- end run it -->
