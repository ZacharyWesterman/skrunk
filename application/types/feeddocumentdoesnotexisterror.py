"""application.types.feeddocumentdoesnotexisterror"""

from typing import TypedDict


class FeedDocumentDoesNotExistError(TypedDict):
	"""
	An error indicating that the feed document does not exist.
	"""

	## The error message.
	message: str
