"""application.types.booksearchfilter"""

from typing import TypedDict
from bson.objectid import ObjectId


class BookSearchFilter(TypedDict):
	"""
	A filter for searching books.
	All fields are optional, and if none are provided, all books will be returned.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The username of the book owner.
	owner: str | None
	## The title of the book.
	title: str | None
	## The author of the book.
	author: str | None
	## The genre/category of the book.
	genre: str | None
	## Whether the book is shared with someone other than the owner.
	shared: bool | None
