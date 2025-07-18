"""application.types.logresult"""

from typing import TypedDict
from bson.objectid import ObjectId


class LogResult(TypedDict):
	"""
	A type representing the result of a logging operation.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## Whether the logging operation was successful.
	result: bool
