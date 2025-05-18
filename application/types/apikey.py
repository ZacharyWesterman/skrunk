from typing import TypedDict
from datetime import datetime

class APIKey(TypedDict):
	key: str
	description: str
	created: datetime
	perms: list[str]

