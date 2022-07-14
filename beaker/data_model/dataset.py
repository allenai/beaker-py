from datetime import datetime
from typing import Optional, Tuple, Union

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
    description: Optional[str] = None
    author: Account
    created: datetime
    committed: Optional[datetime] = None
    workspace_ref: WorkspaceRef
    source_execution: Optional[str] = None
    storage: Optional[DatasetStorage] = None

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


class Digest:
    SHA256 = "SHA256"

    def __init__(self, digest: Union[str, bytes]):
        def encode(b: bytes) -> str:
            import base64

            return f"{self.SHA256} {base64.standard_b64encode(b).decode()}"

        encoded: str
        if isinstance(digest, bytes):
            encoded = encode(digest)
        else:
            encoded = digest

        self._encoded = encoded

    def __eq__(self, other) -> bool:
        if isinstance(other, Digest):
            return self.decode() == other.decode()
        elif isinstance(other, str):
            return self == Digest(other)
        elif isinstance(other, bytes):
            return self.decode() == other
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self == other

    def __str__(self) -> str:
        return self._encoded

    def __repr__(self) -> str:
        return self._encoded

    def __hash__(self):
        return hash(self._encoded)

    def decode(self) -> bytes:
        """
        Decode a digest into its raw bytes form.
        """
        import base64

        encoded = self._encoded.split(" ", 1)[-1]
        return base64.standard_b64decode(encoded)


class FileInfo(BaseModel, arbitrary_types_allowed=True):
    path: str
    digest: Digest
    updated: datetime

    size: Optional[int] = None
    """
    The size of the file, if known.
    """

    url: Optional[str] = None
    """
    A URL that can be used to directly download the file.
    """

    @validator("digest", pre=True)
    def _validate_digest(cls, v: Union[str, Digest]) -> Digest:
        if isinstance(v, Digest):
            return v
        else:
            return Digest(v)


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
