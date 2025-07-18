"""application.types.insufficientperms"""

from typing import TypedDict
from bson.objectid import ObjectId


class InsufficientPerms(TypedDict):
	"""
	An error indicating that the user does not have sufficient permissions to perform the action.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The error message
	message: str
