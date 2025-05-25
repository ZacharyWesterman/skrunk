"""application.types.itemdoesnotexisterror"""

from typing import TypedDict


class ItemDoesNotExistError(TypedDict):
	"""
	An error indicating that an item does not exist.
	"""

	## The error message
	message: str
