"""application.types.userdoesnotexisterror"""

from typing import TypedDict


class UserDoesNotExistError(TypedDict):
	"""
	An error indicating that the user does not exist.
	"""

	## The error message
	message: str
