"""application.types.booklist"""

from typing import TypedDict
from .book import Book


class BookList(TypedDict):
	"""
	A list of books.
	"""

	## The list of books.
	books: list[Book]
