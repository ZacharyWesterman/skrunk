from typing import TypedDict
from datetime import datetime


class BookOwnerHist(TypedDict):
	user_id: str
	name: str
	display_name: str
	start: datetime
	stop: datetime
