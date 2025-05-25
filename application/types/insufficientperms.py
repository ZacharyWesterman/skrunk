"""application.types.insufficientperms"""

from typing import TypedDict


class InsufficientPerms(TypedDict):
	"""
	An error indicating that the user does not have sufficient permissions to perform the action.
	"""

	## The error message
	message: str
