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

.. autoclass:: beaker.BaseModel

Account
~~~~~~~

.. autoclass:: beaker.Account
   :members:

Organization
~~~~~~~~~~~~

.. autoclass:: beaker.Organization
   :members:

.. autoclass:: beaker.OrganizationRole
   :members:

.. autoclass:: beaker.OrganizationMember
   :members:

Workspace
~~~~~~~~~

.. autoclass:: beaker.Workspace
   :members:

.. autoclass:: beaker.WorkspaceSize
   :members:

.. autoclass:: beaker.WorkspaceRef
   :members:

.. autoclass:: beaker.Permission
   :members:

.. autoclass:: beaker.WorkspacePermissions
   :members:

Cluster
~~~~~~~

.. autoclass:: beaker.Cluster
   :members:

.. autoclass:: beaker.ClusterStatus
   :members:

.. autoclass:: beaker.ClusterUtilization
   :members:

.. autoclass:: beaker.ClusterSpec
   :members:

.. autoclass:: beaker.ClusterPatch
   :members:

Node
~~~~

.. autoclass:: beaker.Node
   :members:

.. autoclass:: beaker.NodeResources
   :members:

.. autoclass:: beaker.NodeUtilization
   :members:

Dataset
~~~~~~~

.. autoclass:: beaker.Dataset
   :members:

.. autoclass:: beaker.DatasetStorage
   :members:

.. autoclass:: beaker.FileInfo
   :members:

.. autoclass:: beaker.Digest
   :members:

.. autoclass:: beaker.DigestHashAlgorithm
   :members:

Image
~~~~~

.. autoclass:: beaker.Image
   :members:

Job
~~~

.. autoclass:: beaker.Job
   :members:

.. autoclass:: beaker.JobKind
   :members:

.. autoclass:: beaker.CurrentJobStatus
   :members:

.. autoclass:: beaker.CanceledCode
   :members:

.. autoclass:: beaker.JobStatus
   :members:

.. autoclass:: beaker.ExecutionResult
   :members:

.. autoclass:: beaker.JobRequests
   :members:

.. autoclass:: beaker.JobExecution
   :members:

.. autoclass:: beaker.JobLimits
   :members:

.. autoclass:: beaker.Session
   :members:

Experiment
~~~~~~~~~~

.. autoclass:: beaker.Experiment
   :members:
   
.. autoclass:: beaker.Task
   :members:

.. autoclass:: beaker.Tasks
   :members:

Secret
~~~~~~

.. autoclass:: beaker.Secret
   :members:

Group
~~~~~

.. autoclass:: beaker.Group
   :members:

Experiment Spec
---------------

ExperimentSpec
~~~~~~~~~~~~~~

.. autoclass:: beaker.ExperimentSpec
   :members:
   :undoc-members:

TaskSpec
~~~~~~~~

.. autoclass:: beaker.TaskSpec
   :members:
   :undoc-members:

ImageSource
~~~~~~~~~~~

.. autoclass:: beaker.ImageSource
   :members:
   :undoc-members:

EnvVar
~~~~~~

.. autoclass:: beaker.EnvVar
   :members:
   :undoc-members:

DataMount
~~~~~~~~~

.. autoclass:: beaker.DataMount
   :members:
   :undoc-members:

DataSource
~~~~~~~~~~

.. autoclass:: beaker.DataSource
   :members:
   :undoc-members:

TaskResources
~~~~~~~~~~~~~

.. autoclass:: beaker.TaskResources
   :members:
   :undoc-members:

TaskContext
~~~~~~~~~~~

.. autoclass:: beaker.TaskContext
   :members:
   :undoc-members:

Constraints
~~~~~~~~~~~

.. autoclass:: beaker.Constraints
   :members:
   :undoc-members:

ResultSpec
~~~~~~~~~~

.. autoclass:: beaker.ResultSpec
   :members:
   :undoc-members:

Priority
~~~~~~~~

.. autoclass:: beaker.Priority
   :members:
   :undoc-members:

SpecVersion
~~~~~~~~~~~

.. autoclass:: beaker.SpecVersion
   :members:
   :undoc-members:

Config
------

.. autoclass:: beaker.Config
   :members:

Exceptions
----------

.. automodule:: beaker.exceptions
   :members:
