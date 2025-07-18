"""application.types.badnotification"""

from typing import TypedDict
from bson.objectid import ObjectId


class BadNotification(TypedDict):
	"""
	An error indicating that a notification could not be sent due to invalid data.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The error message
	message: str
