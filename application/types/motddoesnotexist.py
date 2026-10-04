"""application.types.motddoesnotexist"""

from typing import TypedDict
from bson.objectid import ObjectId


class MotdDoesNotExist(TypedDict):
	## The unique identifier of the document.
	_id: ObjectId
	message: str
