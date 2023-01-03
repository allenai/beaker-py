from datetime import datetime
from typing import Optional, Tuple, Union
from urllib.parse import urlparse

from pydantic import validator

from .account import Account
from .base import BaseModel, BasePage, StrEnum
from .workspace import WorkspaceRef

__all__ = [
    "DatasetStorage",
    "DatasetSize",
    "Dataset",
    "DatasetStorageInfo",
    "DatasetInfo",
    "DatasetInfoPage",
    "Digest",
    "FileInfo",
    "DatasetsPage",
    "DatasetSpec",
    "DatasetPatch",
    "DatasetSort",
]


class DatasetStorage(BaseModel):
    id: str
    token: str
    token_expires: datetime
    address: Optional[str] = None
    url: Optional[str] = None
    urlv2: Optional[str] = None

    @validator("address")
    def _validate_address(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.startswith("fh://"):
            # HACK: fix prior to https://github.com/allenai/beaker/pull/2962
            return v.replace("fh://", "https://", 1)
        else:
            return v

    @property
    def scheme(self) -> Optional[str]:
        return "fh" if self.urlv2 is None else urlparse(self.urlv2).scheme

    @property
    def base_url(self) -> str:
        if self.address is not None:
            return self.address
        elif self.urlv2 is not None:
            return f"https://{urlparse(self.urlv2).netloc}"
        else:
            raise ValueError("Missing field 'urlv2' or 'address'")


class DatasetSize(BaseModel):
    files: int
    bytes: int
    final: Optional[bool] = None
    bytes_human: Optional[str] = None


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
    updated: datetime

    digest: Optional[Digest] = None

    size: Optional[int] = None
    """
    The size of the file, if known.
    """

    IGNORE_FIELDS = {"url"}

    @validator("digest", pre=True)
    def _validate_digest(cls, v: Union[str, Digest, None]) -> Optional[Digest]:
        if isinstance(v, Digest):
            return v
        elif isinstance(v, str):
            return Digest(v)
        else:
            return None


class DatasetsPage(BasePage[Dataset]):
    data: Tuple[Dataset, ...]


class DatasetInfoPage(BasePage[FileInfo]):
    data: Tuple[FileInfo, ...]


class DatasetInfo(BaseModel):
    page: DatasetInfoPage
    size: DatasetSize


class DatasetSpec(BaseModel):
    workspace: Optional[str] = None
    description: Optional[str] = None


class DatasetPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    commit: Optional[bool] = None


class DatasetSort(StrEnum):
    created = "created"
    author = "author"
    dataset_name = "name"
    dataset_name_or_description = "nameOrDescription"
