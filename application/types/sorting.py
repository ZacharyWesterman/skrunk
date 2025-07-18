"""application.types.sorting"""

from typing import TypedDict
from bson.objectid import ObjectId


class Sorting(TypedDict):
	"""
	An input type for sorting results in queries.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The fields to sort by, in order of precedence.
	fields: list[str]
	## Whether to sort in descending order. If false, sorting will be in ascending order.
	descending: bool
