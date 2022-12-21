from datetime import datetime
from typing import Optional, Tuple

from pydantic import validator

from .account import Account
from .base import BaseModel, BasePage, StrEnum
from .workspace import WorkspaceRef

__all__ = [
    "Image",
    "ImagesPage",
    "ImageRepoAuth",
    "ImageRepo",
    "DockerLayerProgress",
    "DockerLayerUploadStatus",
    "DockerLayerDownloadStatus",
    "DockerLayerUploadState",
    "DockerLayerDownloadState",
    "ImageSpec",
    "ImagePatch",
    "ImageSort",
]


class Image(BaseModel):
    id: str
    original_tag: str
    owner: Account
    author: Account
    created: datetime
    workspace_ref: WorkspaceRef
    name: Optional[str] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    committed: Optional[datetime] = None
    size: Optional[int] = None

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


class ImagesPage(BasePage[Image]):
    data: Tuple[Image, ...]


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


class DockerLayerUploadStatus(StrEnum):
    preparing = "preparing"
    waiting = "waiting"
    pushing = "pushing"
    pushed = "pushed"
    already_exists = "layer already exists"


class DockerLayerDownloadStatus(StrEnum):
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
    progress: Optional[str] = None

    @validator("status", pre=True)
    def _validate_status(cls, v: str) -> str:
        return v.lower()


class DockerLayerDownloadState(BaseModel):
    id: str
    status: DockerLayerDownloadStatus
    progress_detail: DockerLayerProgress
    progress: Optional[str] = None

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


class ImageSort(StrEnum):
    created = "created"
    author = "author"
    image_name = "name"
