"""application.types.invalidfeedkinderror"""

from typing import TypedDict


class InvalidFeedKindError(TypedDict):
	"""
	An error indicating that the chosen feed kind is invalid.
	"""

	## The error message.
	message: str
