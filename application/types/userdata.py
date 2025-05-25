"""application.types.userdata"""

from typing import TypedDict
from .usertheme_ import UserTheme_
from datetime import datetime


class UserData(TypedDict):
	"""
	Data for a user in the system.
	"""

	## The username of the user.
	username: str
	## The display name of the user.
	display_name: str
	## The theme settings for the user.
	theme: UserTheme_
	## The permissions assigned to the user.
	perms: list[str]
	## The date and time when the user last logged in, if ever.
	last_login: datetime | None
	## A list of groups the user belongs to.
	groups: list[str]
	## A list of modules the user has disabled for themselves.
	disabled_modules: list[str]
	## The user's email address. This is currently reserved for possible future use.
	email: str
