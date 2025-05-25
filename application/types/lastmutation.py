from typing import TypedDict
from datetime import datetime


class LastMutation(TypedDict):
	username: str | None
	request: str
	timestamp: datetime
