"""application.types.bookident"""

from typing import TypedDict
from bson.objectid import ObjectId


class BookIdent(TypedDict):
	"""
	An industry identifier for a book, such as ISBN.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The type of identifier, e.g., ISBN_10, ISBN_13.
	type: str
	## The identifier value.
	identifier: str
