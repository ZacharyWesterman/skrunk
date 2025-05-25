"""application.types.badusernameerror"""

from typing import TypedDict


class BadUserNameError(TypedDict):
	"""
	An error indicating that the chosen username is invalid.
	"""

	## The error message
	message: str
