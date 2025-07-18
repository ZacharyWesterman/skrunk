"""application.types.userbookcount"""

from typing import TypedDict
from bson.objectid import ObjectId
from .usermindata import UserMinData


class UserBookCount(TypedDict):
	"""
	Book count information for a user.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## Minimal user data for the owner of the books.
	owner: UserMinData
	## The total number of books owned by the user.
	count: int
