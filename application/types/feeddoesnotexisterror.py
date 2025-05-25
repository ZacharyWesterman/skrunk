"""application.types.feeddoesnotexisterror"""

from typing import TypedDict


class FeedDoesNotExistError(TypedDict):
	"""
	An error indicating that a data feed does not exist.
	"""

	## The error message.
	message: str
