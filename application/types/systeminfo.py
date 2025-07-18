"""application.types.systeminfo"""

from typing import TypedDict
from bson.objectid import ObjectId
from .diskusage import DiskUsage


class SystemInfo(TypedDict):
	"""
	System information about the server.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## A list usage statistics for each discrete disk on the server.
	storage: list[DiskUsage]
