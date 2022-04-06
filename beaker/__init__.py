"""
Accounts
--------

Manage your Beaker account with :data:`Beaker.account`.

For example, you can check who you are logged in as with
:meth:`Beaker.account.whoami() <services.AccountClient.whoami>`:

>>> username = beaker.account.whoami().name

Organizations
-------------

Manage Beaker organizations with :data:`Beaker.organization`.

For example, you can get information about an organization with
:meth:`Beaker.organization.get() <services.OrganizationClient>`:

>>> beaker.organization.get(beaker_org_name).display_name
'AI2'

Workspaces
----------

Manage Beaker workspaces with :data:`Beaker.workspace`.

For example, you can create a workspace with :meth:`Beaker.workspace.ensure() <services.WorkspaceClient.ensure>`:

>>> beaker.workspace.ensure(workspace_name)

And you can retreive metadata about a workspace with :meth:`Beaker.workspace.get() <services.WorkspaceClient.get>`:

>>> beaker.workspace.get(workspace_name).id
'01FPB5S64Y649S1948QHQHVCVE'

Clusters
--------

Manage Beaker clusters with :data:`Beaker.cluster`.

For example, you can get information about a cluster with
:meth:`Beaker.cluster.get() <services.ClusterClient.get>`:

>>> beaker.cluster.get(beaker_cluster_name).autoscale
True

Images
------

Manage Beaker images with :data:`Beaker.image`.

For example, upload a local Docker image to Beaker with
:meth:`Beaker.image.create() <services.ImageClient.create>`:

>>> image = beaker.image.create(beaker_image_name, docker_image_name, quiet=True)
<BLANKLINE>

The object returned is the same :class:`~data_model.Image` object you get from
:meth:`Beaker.image.get() <services.ImageClient.get>`.
It contains some metadata about the image:

>>> image = beaker.image.get(f"{username}/{beaker_image_name}")
>>> image.original_tag
'hello-world'

Experiments
-----------

Manage Beaker experiments with :data:`Beaker.experiment`.

For example, create an experiment with :meth:`Beaker.experiment.create() <services.ExperimentClient.create>`:

>>> spec = ExperimentSpec(
...     tasks=[
...         TaskSpec(
...             name="main",
...             image=ImageSource(beaker=image.id),
...             context=TaskContext(cluster=beaker_cluster_name),
...             result=ResultSpec(
...                 path="/unused"  # required even if the task produces no output.
...             ),
...         ),
...     ],
... )
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

Get the logs from the experiment with :meth:`Beaker.experiment.logs() <services.ExperimentClient.logs>`:

>>> logs = "".join([
...    line.decode() for line in
...    beaker.experiment.logs(experiment.full_name, quiet=True)
... ])
<BLANKLINE>

Datasets
--------

Manage Beaker datasets with :data:`Beaker.dataset`.

For example, create a dataset from a local file with
:meth:`Beaker.dataset.create() <services.DatasetClient.create>`:

>>> dataset = beaker.dataset.create(dataset_name, "README.md", quiet=True)
<BLANKLINE>

Or create a dataset from a local directory:

>>> dataset = beaker.dataset.create(dataset_name, "docs/source/", force=True, quiet=True)
<BLANKLINE>

.. tip::
    The ``force=True`` flag is used to overwrite any existing dataset with the same name.

And download a dataset with :meth:`Beaker.dataset.fetch() <services.DatasetClient.fetch>`:

>>> beaker.dataset.fetch(dataset, target=download_path, quiet=True)
<BLANKLINE>

"""

from .client import *
from .config import *
from .data_model import *
from .exceptions import *
