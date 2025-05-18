from typing import TypedDict
from datetime import datetime
from .usermindata import UserMinData
from .blob import Blob

class Item(TypedDict):
	id: str
	created: datetime
	creator: UserMinData | None
	owner: UserMinData | None
	category: str
	type: str
	location: str
	blob: Blob | None
	description: str
	description_html: str
	rfid: list[str]

