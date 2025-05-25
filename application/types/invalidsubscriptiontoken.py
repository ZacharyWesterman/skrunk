"""application.types.invalidsubscriptiontoken"""

from typing import TypedDict


class InvalidSubscriptionToken(TypedDict):
	"""
	An error indicating that the user's WebPush subscription token is invalid.
	"""

	## The error message
	message: str
