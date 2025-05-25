"""application.types.webpushexception"""

from typing import TypedDict


class WebPushException(TypedDict):
	"""
	An error indicating that a user could not be notified because of a WebPush error.
	"""

	## The error message
	message: str
