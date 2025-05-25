"""application.types.booktagexistserror"""

from typing import TypedDict


class BookTagExistsError(TypedDict):
	"""
	Error thrown when trying to tag a book that already exists.
	"""

	## Message indicating that the book tag already exists.
	message: str
