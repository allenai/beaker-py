"""
Accounts
--------

Manage your Beaker account with :data:`Beaker.account`.

For example, you can check who you are logged in as with
:meth:`Beaker.account.whoami() <client.AccountClient.whoami>`:

>>> username = beaker.account.whoami().name

Workspaces
----------

Manage Beaker workspaces with :data:`Beaker.workspace`.

For example, you can create a workspace with :meth:`Beaker.workspace.ensure() <client.WorkspaceClient.ensure>`:

>>> beaker.workspace.ensure(workspace_name)

And you can retreive metadata about a workspace with :meth:`Beaker.workspace.get() <client.WorkspaceClient.get>`:

>>> beaker.workspace.get(workspace_name).id
'01FPB5S64Y649S1948QHQHVCVE'

Images
------

Manage Beaker images with :data:`Beaker.image`.

For example, upload a local Docker image to Beaker with :meth:`Beaker.image.create() <client.ImageClient.create>`:

>>> image = beaker.image.create(beaker_image_name, docker_image_name, quiet=True)
<BLANKLINE>

The object returned is the same :class:`~data_model.Image` object you get from
:meth:`Beaker.image.get() <client.ImageClient.get>`.
It contains some metadata about the image:

>>> image = beaker.image.get(f"{username}/{beaker_image_name}")
>>> image.original_tag
'hello-world'

Experiments
-----------

Manage Beaker experiments with :data:`Beaker.experiment`.

For example, create an experiment with :meth:`Beaker.experiment.create() <client.ExperimentClient.create>`:

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
>>> experiment = beaker.experiment.create(
...     experiment_name,
...     spec,
...     workspace=workspace_name,
... )

Wait for the experiment to complete:

>>> experiment = beaker.experiment.await_all(
...     experiment.full_name,
...     timeout=60 * 3,
...     quiet=True,
... )
<BLANKLINE>

Get the logs from the experiment with :meth:`Beaker.experiment.logs() <client.ExperimentClient.logs>`:

>>> logs = "".join([
...    line.decode() for line in
...    beaker.experiment.logs(experiment.full_name, quiet=True)
... ])
<BLANKLINE>

Datasets
--------

Manage Beaker datasets with :data:`Beaker.dataset`.

For example, create a dataset from a local file with :meth:`Beaker.dataset.create() <client.DatasetClient.create>`:

>>> dataset = beaker.dataset.create(dataset_name, "README.md", quiet=True)
<BLANKLINE>

Or create a dataset from a local directory:

>>> dataset = beaker.dataset.create(dataset_name, "docs/source/", force=True, quiet=True)
<BLANKLINE>

.. tip::
    The ``force=True`` flag is used to overwrite any existing dataset with the same name.

"""

from .client import Beaker
from .config import Config
from .data_model import *
from .exceptions import *
