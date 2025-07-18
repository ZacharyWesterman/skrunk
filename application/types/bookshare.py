"""application.types.bookshare"""

from typing import TypedDict
from bson.objectid import ObjectId
from datetime import datetime


class BookShare(TypedDict):
	"""
	Sharing information for a book.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The ID of the user the book is shared with, or null if shared with a non-user.
	user_id: str | None
	## The name of the person who the book is shared with.
	name: str
	## The display name of the person who the book is shared with.
	display_name: str
	## The start date and time of the sharing period.
	start: datetime
	## The end date and time of the sharing period, or null if the book isstill being shared.
	stop: datetime | None
