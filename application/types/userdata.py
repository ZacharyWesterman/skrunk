from typing import TypedDict
from .usertheme_ import UserTheme_
from datetime import datetime


class UserData(TypedDict):
	username: str
	display_name: str
	theme: UserTheme_ | None
	perms: list[str]
	last_login: datetime
	groups: list[str]
	disabled_modules: list[str]
	email: str
