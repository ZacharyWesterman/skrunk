from typing import TypedDict
from .blob import Blob

class BlobList(TypedDict):
	blobs: list[Blob | None]

