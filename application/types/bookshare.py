"""application.types.bookshare"""

from typing import TypedDict
from datetime import datetime


class BookShare(TypedDict):
	user_id: str | None
	name: str
	display_name: str
	start: datetime
	stop: datetime | None
