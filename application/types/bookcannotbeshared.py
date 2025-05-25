"""application.types.bookcannotbeshared"""

from typing import TypedDict


class BookCannotBeShared(TypedDict):
	"""
	Error thrown when a book cannot be shared.
	"""

	## Message indicating that the book cannot be shared.
	message: str
