"""application.types.itemexistserror"""

from typing import TypedDict


class ItemExistsError(TypedDict):
	"""
	An error indicating that an item already exists.
	"""

	## The error message
	message: str
