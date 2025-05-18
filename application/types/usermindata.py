from typing import TypedDict
from datetime import datetime


class UserMinData(TypedDict):
	username: str
	display_name: str
	last_login: datetime
