"""
Accounts
--------

Manage your Beaker account with :data:`Beaker.account`.

For example, you can check who you are logged in as with
:meth:`Beaker.account.whoami() <services.AccountClient.whoami>`:

>>> username = beaker.account.whoami().name

.. important::
    In this example - and all other examples - ``beaker`` is an instance of the
    :class:`Beaker` client class, not the :mod:`beaker` module.
    See `Quick start <./quickstart.html>`_ to learn how to instantiate the client.

Organizations
-------------

Manage Beaker organizations with :data:`Beaker.organization`.

For example, you can get information about an organization with
:meth:`Beaker.organization.get() <services.OrganizationClient.get>`:

>>> beaker.organization.get(beaker_org_name).display_name
'AI2'

You can also add, get, list, or remove members with
:meth:`Beaker.organization.add_member() <services.OrganizationClient.add_member>`,
:meth:`.get_member() <services.OrganizationClient.get_member>`,
:meth:`.list_members() <services.OrganizationClient.list_members>`, or
:meth:`.remove_member() <services.OrganizationClient.remove_member>`, respectively.

Workspaces
----------

Manage Beaker workspaces with :data:`Beaker.workspace`.

For example, you can create a workspace with :meth:`Beaker.workspace.ensure() <services.WorkspaceClient.ensure>`:

>>> workspace = beaker.workspace.ensure(workspace_name)

You can retreive metadata about a workspace with :meth:`Beaker.workspace.get() <services.WorkspaceClient.get>`:

>>> beaker.workspace.get(workspace_name).id
'01G370GVHJQZYF50XYXM7VB53N'

You can list datasets in a workspace with
:meth:`Beaker.workspace.datasets() <services.WorkspaceClient.datasets>`:

>>> datasets = beaker.workspace.datasets(workspace_name, results=False)

Similarly, you can list experiments or images with
:meth:`Beaker.workspace.experiments() <services.WorkspaceClient.experiments>`
or
:meth:`Beaker.workspace.images() <services.WorkspaceClient.images>`,
respectively.

Clusters
--------

Manage Beaker clusters with :data:`Beaker.cluster`.

For example, you can get information about a cluster with
:meth:`Beaker.cluster.get() <services.ClusterClient.get>`:

>>> beaker.cluster.get(beaker_cloud_cluster_name).autoscale
True

Or you could check how many GPUs are free on an on-premise cluster with
:meth:`Beaker.cluster.utilization() <services.ClusterClient.utilization>`:

>>> free_gpus = 0
>>> for node_util in beaker.cluster.utilization(beaker_on_prem_cluster_name).nodes:
...     free_gpus += node_util.free.gpu_count

Nodes
-----

Manage Beaker nodes with :data:`Beaker.node`.

For example, you can get information about a node with
:meth:`Beaker.node.get() <services.NodeClient.get>`:

>>> beaker.node.get(beaker_node_id).limits.gpu_count
8

Images
------

Manage Beaker images with :data:`Beaker.image`.

For example, upload a local Docker image to Beaker with
:meth:`Beaker.image.create() <services.ImageClient.create>`:

>>> image = beaker.image.create(beaker_image_name, docker_image_name, quiet=True)
<BLANKLINE>

The object returned is the same :class:`~data_model.image.Image` object you get from
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

Wait for the experiment to complete with
:meth:`Beaker.experiment.wait_for() <services.ExperimentClient.wait_for>`:

>>> experiment = beaker.experiment.wait_for(
...     experiment,
...     timeout=60 * 5,
...     quiet=True,
... )[0]

Get the logs from the execution of a task in an experiment with
:meth:`Beaker.experiment.logs() <services.ExperimentClient.logs>`:

>>> logs = "".join([
...    line.decode() for line in
...    beaker.experiment.logs(experiment, quiet=True)
... ])
<BLANKLINE>

Get the results from a task in an experiment with
:meth:`Beaker.experiment.results <services.ExperimentClient.results>`:

>>> results = beaker.experiment.results(experiment)

Jobs
----

Manage Beaker jobs with :data:`Beaker.job`.

For example, get the logs from a job with :meth:`Beaker.job.logs() <services.JobClient.logs>`
(equivalent to :meth:`Beaker.experiment.logs() <services.ExperimentClient.logs>` when there is
only one task in the experiment):

>>> job = experiment.jobs[0]
>>> logs = "".join([
...    line.decode() for line in
...    beaker.job.logs(job, quiet=True)
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

Secrets
-------

Manage Beaker secrets with :data:`Beaker.secret`.

For example, you can read, write, or delete secrets with
:meth:`Beaker.secret.read() <services.SecretClient.read>`,
:meth:`Beaker.secret.write() <services.SecretClient.write>`, and
:meth:`Beaker.secret.delete() <services.SecretClient.delete>`, respectively.

Groups
------

Manage Beaker groups with :data:`Beaker.group`.

For example, create a group with :meth:`Beaker.group.create() <services.GroupClient.create>`:

>>> group = beaker.group.create(group_name, experiment)

"""

from .client import *
from .config import *
from .data_model import *
from .exceptions import *
