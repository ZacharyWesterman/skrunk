"""application.types.userexistserror"""

from typing import TypedDict


class UserExistsError(TypedDict):
	"""
	An error indicating that the user already exists.
	"""

	## The error message
	message: str
