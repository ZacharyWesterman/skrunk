from typing import TypedDict
from datetime import datetime

class LastMutation(TypedDict):
	username: str
	request: str
	timestamp: datetime

