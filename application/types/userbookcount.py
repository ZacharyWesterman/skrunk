"""application.types.userbookcount"""

from typing import TypedDict
from .usermindata import UserMinData


class UserBookCount(TypedDict):
	"""
	Book count information for a user.
	"""

	## Minimal user data for the owner of the books.
	owner: UserMinData
	## The total number of books owned by the user.
	count: int
