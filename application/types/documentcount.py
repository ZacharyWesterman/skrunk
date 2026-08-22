"""application.types.documentcount"""

from typing import TypedDict
from bson.objectid import ObjectId


class DocumentCount(TypedDict):
	"""
	A type for getting the number of documents that match a query.
	This type is used so that if the query fails, we can return an error message instead of zero.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The number of documents that match the query
	count: int
