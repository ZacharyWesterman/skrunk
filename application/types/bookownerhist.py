"""application.types.bookownerhist"""

from typing import TypedDict
from datetime import datetime


class BookOwnerHist(TypedDict):
	"""
	Owner history information for a book.
	"""

	## The ID of the user who owned the book.
	user_id: str
	## The name of the user who owned the book.
	name: str
	## The display name of the user who owned the book.
	display_name: str
	## The date and time when the book started being owned by this user.
	start: datetime
	## The date and time when the book stopped being owned by this user.
	stop: datetime
