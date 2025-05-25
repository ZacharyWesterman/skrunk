"""application.types.bugreportdoesnotexisterror"""

from typing import TypedDict


class BugReportDoesNotExistError(TypedDict):
	"""
	An error indicating that a bug report does not exist.
	"""

	## The error message.
	message: str
