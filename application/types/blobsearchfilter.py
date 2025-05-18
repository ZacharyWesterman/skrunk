from typing import TypedDict
from datetime import datetime

class BlobSearchFilter(TypedDict):
	creator: str
	begin_date: datetime
	end_date: datetime
	name: str
	tag_expr: str
	ephemeral: bool

