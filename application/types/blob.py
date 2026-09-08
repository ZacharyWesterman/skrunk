"""application.types.blob"""

from typing import TypedDict
from bson.objectid import ObjectId
from datetime import datetime


class Blob(TypedDict):
	"""
	A type for blob data.
	"""

	## The unique identifier of the document.
	_id: ObjectId
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
	## A list of preview URLs (or IDs if hosted in-situ) for the blob. - For images, this will contain a smaller, compressed version of the image. - For videos, this will contain a low-res copy of the video in one or more formats. - For 3d models, it's a version that can be easily rendered in a browser.
	previews: list[str]
	## The thumbnail URL (or ID if hosted in-situ) for the blob. This is always a very small preview image.
	thumbnail: str | None
	## Whether the blob is restricted to only the user who created it.
	hidden: bool
	## Whether the blob is ephemeral. Ephemeral blobs are deleted after a certain amount of time.
	ephemeral: bool
	## The number of other documents that reference this blob. If ephemeral, this is used to determine if the blob can be deleted.
	references: int
	## Whether the blob has finished uploading and being processed.
	complete: bool
