"""application.types.bookeditdata"""

from typing import TypedDict
from bson.objectid import ObjectId


class BookEditData(TypedDict):
	"""
	Modified data for a book, used when editing a book entry.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The title of the book.
	title: str
	## The subtitle of the book, if any.
	subtitle: str | None
	## The book authors.
	authors: list[str]
