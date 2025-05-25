"""application.types.userdata"""

from typing import TypedDict
from .usertheme_ import UserTheme_
from datetime import datetime


class UserData(TypedDict):
	username: str
	display_name: str
	theme: UserTheme_
	perms: list[str]
	last_login: datetime | None
	groups: list[str]
	disabled_modules: list[str]
	email: str
