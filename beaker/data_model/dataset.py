from datetime import datetime
from typing import ClassVar, Optional, Tuple, Union
from urllib.parse import urlparse

from pydantic import validator

from .account import Account
from .base import BaseModel, BasePage, StrEnum
from .workspace import WorkspaceRef

__all__ = [
    "DatasetStorage",
    "DatasetSize",
    "Dataset",
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


class Digest(BaseModel):
    value: str
    """
    The hex-encoded value of the digest.
    """

    algorithm: str
    """
    The algorithm used to create and verify the digest.
    """

    SHA256: ClassVar[str] = "SHA256"

    @classmethod
    def from_encoded(cls, encoded: str) -> "Digest":
        """
        Initialize a digest from a raw encoding of the form "{ALGORITHM} {ENCODED_STRING}".
        """
        import base64
        import binascii

        algorithm, value_b64 = encoded.split(" ", 1)
        value_bytes = base64.standard_b64decode(value_b64)
        value = binascii.hexlify(value_bytes).decode()
        return cls(value=value, algorithm=algorithm)

    @classmethod
    def from_decoded(cls, decoded: bytes, algorithm: str) -> "Digest":
        """
        Initialize a digest from raw decoded bytes.
        """
        import binascii

        value = binascii.hexlify(decoded).decode()
        return Digest(value=value, algorithm=algorithm)

    def encode(self) -> str:
        """
        Encode the digest into its string form.

        This is the inverse of :meth:`.from_encoded()`.
        """
        import base64
        import binascii

        value_bytes = binascii.unhexlify(self.value)
        value_b64 = base64.standard_b64encode(value_bytes).decode()

        return f"{self.algorithm} {value_b64}"

    def __hash__(self):
        return hash(self.encode())

    def decode(self) -> bytes:
        """
        Decode a digest into its raw bytes form.

        This is the inverse of :meth:`.from_decoded()`.
        """
        import binascii

        return binascii.unhexlify(self.value)


class FileInfo(BaseModel, arbitrary_types_allowed=True):
    path: str
    """
    The path of the file within the dataset.
    """

    updated: datetime
    """
    The time that the file was last updated.
    """

    digest: Optional[Digest] = None
    """
    The digest of the contents of the file.
    """

    size: Optional[int] = None
    """
    The size of the file in bytes, if known.
    """

    IGNORE_FIELDS = {"url"}

    @validator("digest", pre=True)
    def _validate_digest(cls, v: Union[str, Digest, None]) -> Optional[Digest]:
        if isinstance(v, Digest):
            return v
        elif isinstance(v, str):
            return Digest.from_encoded(v)
        elif isinstance(v, dict):
            return Digest(**v)
        else:
            raise ValueError(f"Unexpected value for 'digest': {v}")


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
