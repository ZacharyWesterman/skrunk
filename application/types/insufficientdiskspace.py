from typing import TypedDict


class InsufficientDiskSpace(TypedDict):
	"""
	An error that occurs when there is insufficient disk space to perform a file operation.
	"""

	## The error message
	message: str
