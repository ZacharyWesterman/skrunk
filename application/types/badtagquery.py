"""application.types.badtagquery"""

from typing import TypedDict
from bson.objectid import ObjectId


class BadTagQuery(TypedDict):
	"""
	An error that occurs when a tag query has invalid syntax.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The error message
	message: str
