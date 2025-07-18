"""application.types.booklist"""

from typing import TypedDict
from bson.objectid import ObjectId
from .book import Book


class BookList(TypedDict):
	"""
	A list of books.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The list of books.
	books: list[Book]
