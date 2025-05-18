from typing import TypedDict
from datetime import datetime
from .sorting_ import Sorting_


class Feed(TypedDict):
	id: str
	name: str
	creator: str
	created: datetime
	kind: str
	url: str
	notify: bool
	inactive: bool
	currentPage: int
	currentSort: Sorting_ | None
