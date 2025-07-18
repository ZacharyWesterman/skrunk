"""application.types.diskusage"""

from typing import TypedDict
from bson.objectid import ObjectId


class DiskUsage(TypedDict):
	"""
	Information about disk usage on the server.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## A descriptive name for the disk.
	name: str
	## The total size of the disk in bytes.
	total: float
	## The amount of free space on the disk in bytes.
	free: float
	## The amount of space used on the disk in bytes.
	used: float
