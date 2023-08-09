__all__ = ['BookSearchFilter']

from typing import TypedDict
from datetime import datetime

class BookSearchFilter(TypedDict):
	owner: str|None
	title: str|None
	author: str|None
	genre: str|None
	shared: bool|None

class BlobSearchFilter(TypedDict):
	creator: str|None
	begin_date: datetime|None
	end_date: datetime|None
	name: str|None
	tag_expr: str|None