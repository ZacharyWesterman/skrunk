"""application.types.booktagdoesnotexisterror"""

from typing import TypedDict


class BookTagDoesNotExistError(TypedDict):
	"""
	Error thrown when a book does not exist.
	"""

	## Message indicating that the book tag does not exist.
	message: str
