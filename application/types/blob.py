from typing import TypedDict
from datetime import datetime


class Blob(TypedDict):
	"""
	A type for blob data.
	"""

	## The ID of the blob
	id: str
	## The date the blob was created
	created: datetime
	## The username of the user who created the blob
	creator: str
	## The original filename of the blob
	name: str
	## The extension of the blob
	ext: str
	## The mime type of the blob
	mimetype: str
	## The size of the blob in bytes
	size: int
	## A list of tags associated with the blob
	tags: list[str]
	## A preview URL or ID for the blob. For images, this is a smaller version of the image. For videos, it's the first frame. For 3d models, it's a version that can be easily rendered in a browser.
	preview: str
	## The thumbnail for the blob. This is a smaller version of the preview, used for displaying in lists, and is always an image.
	thumbnail: str
	## Whether the blob is restricted to only the user who created it.
	hidden: bool
	## Whether the blob is ephemeral. Ephemeral blobs are deleted after a certain amount of time.
	ephemeral: bool
	## The number of other documents that reference this blob. If ephemeral, this is used to determine if the blob can be deleted.
	references: int
