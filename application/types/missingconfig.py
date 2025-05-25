"""application.types.missingconfig"""

from typing import TypedDict


class MissingConfig(TypedDict):
	"""
	An error indicating that a required config item is missing.
	"""

	## The error message
	message: str
