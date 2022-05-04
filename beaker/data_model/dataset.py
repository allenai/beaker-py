from datetime import datetime
from typing import Optional, Tuple

from pydantic import validator

from .account import Account
from .base import BaseModel
from .workspace import WorkspaceRef


class DatasetStorage(BaseModel):
    id: str
    address: str
    token: str
    token_expires: datetime


class DatasetSize(BaseModel):
    final: bool
    files: int
    bytes: int
    bytes_human: str


class Dataset(BaseModel):
    id: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    owner: Account
    author: Account
    created: datetime
    committed: Optional[datetime] = None
    workspace_ref: WorkspaceRef
    storage: Optional[DatasetStorage] = None

    @property
    def display_name(self) -> str:
        return self.name if self.name is not None else self.id

    @validator("committed")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v


class DatasetStorageInfo(BaseModel):
    id: str
    created: Optional[datetime] = None
    size: Optional[DatasetSize] = None
    readonly: bool = True

    @validator("created")
    def _validate_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.year == 1:
            return None
        return v


class FileInfo(BaseModel):
    path: str
    digest: str
    updated: datetime

    size: Optional[int] = None
    """
    The size of the file, if known.
    """

    url: Optional[str] = None
    """
    A URL that can be used to directly download the file.
    """


class DatasetManifest(BaseModel):
    files: Tuple[FileInfo, ...]
    cursor: Optional[str] = None


class DatasetsPage(BaseModel):
    data: Tuple[Dataset, ...]
    next_cursor: Optional[str] = None


class DatasetSpec(BaseModel):
    workspace: Optional[str] = None
    description: Optional[str] = None
    fileheap: Optional[bool] = None


class DatasetPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    commit: Optional[bool] = None
