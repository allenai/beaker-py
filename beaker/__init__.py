"""
User
----

You can check who you are logged in as with :data:`Beaker.user`:

>>> beaker.user
'petew'

Or get more information about your account with :meth:`Beaker.whoami()`:

>>> beaker.whoami().institution
'AllenAI'

Workspaces
----------

You can create a workspace with :meth:`Beaker.ensure_workspace()`:

>>> beaker.ensure_workspace(workspace_name)

And you can retreive metadata about a workspace with :meth:`Beaker.get_workspace()`:

>>> beaker.get_workspace(workspace_name).id
'01FPB5S64Y649S1948QHQHVCVE'

Images
------

Upload a local Docker image to Beaker with :meth:`Beaker.create_image()`:

>>> image = beaker.create_image(beaker_image_name, docker_image_name, quiet=True)
<BLANKLINE>

The object returned is the same :class:`~data_model.Image` object you get from :meth:`Beaker.get_image()`.
It contains some metadata about the image:

>>> image = beaker.get_image(f"{beaker.user}/{beaker_image_name}")
>>> image.original_tag
'hello-world'

Experiments
-----------

Create an experiment with :meth:`Beaker.create_experiment()`:

>>> spec = {
...     "version": "v2-alpha",
...     "tasks": [
...         {
...             "name": "main",
...             "image": {"beaker": image.id},
...             "context": {"cluster": beaker_cluster_name},
...             "result": {
...                 "path": "/unused"  # required even if the task produces no output.
...             },
...             "command": None,
...             "arguments": None,
...         },
...     ],
... }
>>> experiment = beaker.create_experiment(experiment_name, spec, workspace=workspace_name)

Wait for the experiment to complete:

>>> while True:
...    experiment = beaker.get_experiment(experiment.full_name)
...    if experiment.executions and experiment.executions[0].state.exit_code is not None:
...        break
...    else:
...        import time
...        time.sleep(2)

Get the logs from the experiment with :meth:`Beaker.get_logs_for_experiment()`:

>>> logs = "".join([
...    line.decode() for line in
...    beaker.get_logs_for_experiment(experiment.full_name, quiet=True)
... ])
<BLANKLINE>

Datasets
--------

Create a dataset from a local file with :meth:`Beaker.create_dataset()`:

>>> dataset = beaker.create_dataset(dataset_name, "README.md")

"""

from .client import Beaker
from .config import Config
from .data_model import *
from .exceptions import *
