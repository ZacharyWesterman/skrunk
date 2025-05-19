from typing import TypedDict


class BlobDoesNotExistError(TypedDict):
	"""
	An error that occurs when attempting to access a blob that does not exist.
	"""

	## The error message
	message: str
