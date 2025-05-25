"""application.types.badnotification"""

from typing import TypedDict


class BadNotification(TypedDict):
	"""
	An error indicating that a notification could not be sent due to invalid data.
	"""

	## The error message
	message: str
