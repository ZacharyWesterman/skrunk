from typing import TypedDict
from datetime import datetime


class Notification(TypedDict):
	recipient: str
	created: datetime
	message: str
	category: str
	device_count: int
	read: bool
	id: str
