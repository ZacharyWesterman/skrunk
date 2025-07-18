"""application.types.bugreportcreationfailederror"""

from typing import TypedDict
from bson.objectid import ObjectId


class BugReportCreationFailedError(TypedDict):
	"""
	An error indicating that creating a bug report failed.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The error message.
	message: str
