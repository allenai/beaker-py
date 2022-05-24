from datetime import datetime
from enum import Enum
from typing import Optional, Tuple

from pydantic import validator

from .account import Account
from .base import BaseModel
from .workspace import WorkspaceRef


class Image(BaseModel):
    id: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    original_tag: str
    owner: Account
    author: Account
    created: datetime
    committed: Optional[datetime] = None
    workspace_ref: WorkspaceRef

    @property
    def display_name(self) -> str:
        return self.name if self.name is not None else self.id

    @property
    def workspace(self) -> WorkspaceRef:
        return self.workspace_ref

    @validator("committed")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v


class ImagesPage(BaseModel):
    data: Tuple[Image, ...]
    next_cursor: Optional[str] = None


class ImageRepoAuth(BaseModel):
    user: str
    password: str
    server_address: str


class ImageRepo(BaseModel):
    image_tag: str
    auth: ImageRepoAuth


class DockerLayerProgress(BaseModel):
    current: Optional[int] = None
    total: Optional[int] = None


class DockerLayerUploadStatus(str, Enum):
    preparing = "preparing"
    waiting = "waiting"
    pushing = "pushing"
    pushed = "pushed"
    already_exists = "layer already exists"


class DockerLayerDownloadStatus(str, Enum):
    waiting = "waiting"
    downloading = "downloading"
    download_complete = "download complete"
    verifying_checksum = "verifying checksum"
    extracting = "extracting"
    pull_complete = "pull complete"
    already_exists = "already exists"


class DockerLayerUploadState(BaseModel):
    id: str
    status: DockerLayerUploadStatus
    progress_detail: DockerLayerProgress

    @validator("status", pre=True)
    def _validate_status(cls, v: str) -> str:
        return v.lower()


class DockerLayerDownloadState(BaseModel):
    id: str
    status: DockerLayerDownloadStatus
    progress_detail: DockerLayerProgress

    @validator("status", pre=True)
    def _validate_status(cls, v: str) -> str:
        return v.lower()


class ImageSpec(BaseModel):
    workspace: Optional[str] = None
    image_id: Optional[str] = None
    image_tag: Optional[str] = None
    description: Optional[str] = None


class ImagePatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    commit: Optional[bool] = None
