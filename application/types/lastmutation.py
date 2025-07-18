"""application.types.lastmutation"""

from typing import TypedDict
from bson.objectid import ObjectId
from datetime import datetime


class LastMutation(TypedDict):
	"""
	Information about the last mutation made by a user.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The username of the user who made the last mutation.
	username: str | None
	## The ID of the last mutation request.
	request: str
	## The date and time when the last mutation was made.
	timestamp: datetime
