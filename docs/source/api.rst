API
===

Client
------

.. autoclass:: beaker.Beaker
   :members:
   :member-order: bysource

Account
~~~~~~~

.. autoclass:: beaker.services.AccountClient
   :members:
   :member-order: bysource

Organization
~~~~~~~~~~~~

.. autoclass:: beaker.services.OrganizationClient
   :members:
   :member-order: bysource

Workspace
~~~~~~~~~

.. autoclass:: beaker.services.WorkspaceClient
   :members:
   :member-order: bysource

Cluster
~~~~~~~

.. autoclass:: beaker.services.ClusterClient
   :members:
   :member-order: bysource

Node
~~~~

.. autoclass:: beaker.services.NodeClient
   :members:
   :member-order: bysource

Dataset
~~~~~~~

.. autoclass:: beaker.services.DatasetClient
   :members:
   :member-order: bysource

Image
~~~~~

.. autoclass:: beaker.services.ImageClient
   :members:
   :member-order: bysource

Job
~~~

.. autoclass:: beaker.services.JobClient
   :members:
   :member-order: bysource

Experiment
~~~~~~~~~~

.. autoclass:: beaker.services.ExperimentClient
   :members:
   :member-order: bysource

Secret
~~~~~~

.. autoclass:: beaker.services.SecretClient
   :members:
   :member-order: bysource

Group
~~~~~

.. autoclass:: beaker.services.GroupClient
   :members:
   :member-order: bysource

Data Models
-----------

.. automodule:: beaker.data_model

.. autoclass:: beaker.data_model.base.BaseModel

Account
~~~~~~~

.. automodule:: beaker.data_model.account
   :members:
   :undoc-members:

Organization
~~~~~~~~~~~~

.. automodule:: beaker.data_model.organization
   :members:
   :undoc-members:

Workspace
~~~~~~~~~

.. autoclass:: beaker.data_model.workspace.Workspace
   :members:
   :undoc-members:

.. automodule:: beaker.data_model.workspace
   :members: WorkspaceSize, WorkspaceRef, Permission, WorkspacePermissions
   :undoc-members:

Cluster
~~~~~~~

.. autoclass:: beaker.data_model.cluster.Cluster
   :members:
   :undoc-members:

.. automodule:: beaker.data_model.cluster
   :members:
   :undoc-members:
   :exclude-members: Cluster

Node
~~~~

.. autoclass:: beaker.data_model.node.Node
   :members:
   :undoc-members:

.. automodule:: beaker.data_model.node
   :members:
   :undoc-members:
   :exclude-members: Node

Dataset
~~~~~~~

.. autoclass:: beaker.data_model.dataset.Dataset
   :members:
   :undoc-members:

.. automodule:: beaker.data_model.dataset
   :members: DatasetStorage, FileInfo, Digest
   :undoc-members:

Image
~~~~~

.. automodule:: beaker.data_model.image
   :members: Image
   :undoc-members:

Job
~~~

.. autoclass:: beaker.data_model.job.Job
   :members:
   :undoc-members:

.. automodule:: beaker.data_model.job
   :members:
   :undoc-members:
   :exclude-members: Job, Jobs

Experiment
~~~~~~~~~~

.. automodule:: beaker.data_model.experiment
   :members: Experiment, Task, Tasks
   :undoc-members:

Secret
~~~~~~

.. automodule:: beaker.data_model.secret
   :members:
   :undoc-members:

Group
~~~~~

.. automodule:: beaker.data_model.group
   :members:
   :undoc-members:

Experiment Spec
---------------

.. autoclass:: beaker.data_model.experiment_spec.ExperimentSpec
   :members:
   :undoc-members:

.. autoclass:: beaker.data_model.experiment_spec.TaskSpec
   :members:
   :undoc-members:

.. automodule:: beaker.data_model.experiment_spec
   :members:
   :undoc-members:
   :exclude-members: ExperimentSpec,TaskSpec

Config
------

.. autoclass:: beaker.Config
   :members:

Exceptions
----------

.. automodule:: beaker.exceptions
   :members:

.. autoexception:: beaker.exceptions.HTTPError

.. autoexception:: beaker.exceptions.ValidationError
