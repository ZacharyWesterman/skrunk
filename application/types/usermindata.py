"""application.types.usermindata"""

from typing import TypedDict
from datetime import datetime


class UserMinData(TypedDict):
	"""
	Minimal data for a user, used for listing users or getting basic user information.
	"""

	## The username of the user.
	username: str
	## The display name of the user.
	display_name: str
	## The date and time when the user last logged in, if ever.
	last_login: datetime | None
