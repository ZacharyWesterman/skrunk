from typing import TypedDict
from .blob import Blob


class BlobList(TypedDict):
	"""
	A list of blobs.
	This type is used so that if the query fails, we can return an error message instead of an empty list.
	"""

	## The blob list
	blobs: list[Blob]
