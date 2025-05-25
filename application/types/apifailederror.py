"""application.types.apifailederror"""

from typing import TypedDict


class ApiFailedError(TypedDict):
	"""
	Error thrown when a Google Books API request fails.
	"""

	## Error message from the API.
	message: str
