"""application.types.zipprogress"""

from typing import TypedDict
from bson.objectid import ObjectId


class ZipProgress(TypedDict):
	"""
	A type for keeping track of the progress of a zip archive creation.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The progress of the zip archive creation. 0-100%
	progress: float
	## The filename of the item being zipped
	item: str
	## If true, the ZIP file is being finalized and will soon be available for download.
	finalizing: bool
