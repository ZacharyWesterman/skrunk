"""application.types.tag"""

from typing import TypedDict
from bson.objectid import ObjectId


class Tag(TypedDict):
	"""
	A type for tag metadata.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The text of the tag
	name: str
	## The number of items that have this tag
	count: int
