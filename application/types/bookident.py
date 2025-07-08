"""application.types.bookident"""

from typing import TypedDict


class BookIdent(TypedDict):
	"""
	An industry identifier for a book, such as ISBN.
	"""

	## The type of identifier, e.g., ISBN_10, ISBN_13.
	type: str
	## The identifier value.
	identifier: str
