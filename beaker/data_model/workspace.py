from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .account import Account
from .base import BaseModel, BasePage, StrEnum, model_validator
from .experiment_spec import Priority
from .organization import Organization

__all__ = [
    "WorkspaceSize",
    "Workspace",
    "WorkspaceRef",
    "WorkspacePage",
    "WorkspaceSpec",
    "WorkspaceTransferSpec",
    "Permission",
    "WorkspacePermissions",
    "WorkspacePatch",
    "WorkspacePermissionsPatch",
    "WorkspaceClearResult",
    "WorkspaceSort",
]


class WorkspaceSize(BaseModel):
    datasets: int = 0
    experiments: int = 0
    groups: int = 0
    images: int = 0
    environments: int = 0


class Workspace(BaseModel):
    id: str
    name: str
    full_name: str
    description: Optional[str] = None
    size: Optional[WorkspaceSize] = None
    owner: Optional[Account] = None
    owner_org: Optional[Organization] = None
    author: Account
    created: datetime
    modified: datetime
    archived: bool = False
    max_workload_priority: Optional[Priority] = None
    budget_id: Optional[str] = None
    slot_limit_preemptible: Optional[int] = None
    slot_limit_non_preemptible: Optional[int] = None
    assigned_slots_preemptible: Optional[int] = None

    @model_validator(mode="before")
    def _adjust_new_field_names_for_compat_with_rpc_api(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        if (
            "maxWorkloadPriority" not in values
            and (priority := values.pop("maximumWorkloadPriority", None)) is not None
        ):
            values["maxWorkloadPriority"] = priority.lower().replace("job_priority_", "")

        values.setdefault("author", values.pop("authorUser", None))

        if (name := values.get("name")) is not None and "/" in name:
            values["name"] = name.split("/")[1]

        if (
            "fullName" not in values
            and (name := values.get("name")) is not None
            and (org := values.get("ownerOrg")) is not None
        ):
            values["fullName"] = f"{org['name']}/{name}"

        return values


class WorkspaceRef(BaseModel):
    id: str
    name: str
    full_name: str


class WorkspacePage(BasePage[Workspace]):
    data: Tuple[Workspace, ...]
    org: Optional[str] = None


class WorkspaceSpec(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    public: Optional[bool] = None
    org: Optional[str] = None


class WorkspaceTransferSpec(BaseModel):
    ids: List[str]


class Permission(StrEnum):
    """
    Workspace permission levels.
    """

    no_permission = "none"
    read = "read"
    write = "write"
    full_control = "all"


class WorkspacePermissions(BaseModel):
    requester_auth: str
    public: bool
    authorizations: Optional[Dict[str, Permission]] = None
    """
    A dictionary of account IDs to authorizations.
    """


class WorkspacePatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    archive: Optional[bool] = None


class WorkspacePermissionsPatch(BaseModel):
    public: Optional[bool] = None
    authorizations: Optional[Dict[str, Permission]] = None


class WorkspaceClearResult(BaseModel):
    groups_deleted: int = 0
    experiments_deleted: int = 0
    images_deleted: int = 0
    datasets_deleted: int = 0
    secrets_deleted: int = 0


class WorkspaceSort(StrEnum):
    created = "created"
    modified = "modified"
    workspace_name = "name"
