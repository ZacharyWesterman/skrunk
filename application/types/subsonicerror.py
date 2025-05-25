"""application.types.subsonicerror"""

from typing import TypedDict


class SubsonicError(TypedDict):
	"""
	An error indicating an issue with the Subsonic API.
	"""

	## The error message
	message: str
