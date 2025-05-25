"""application.types.bugreportcreationfailederror"""

from typing import TypedDict


class BugReportCreationFailedError(TypedDict):
	"""
	An error indicating that creating a bug report failed.
	"""

	## The error message.
	message: str
