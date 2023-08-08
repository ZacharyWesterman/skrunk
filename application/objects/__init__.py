__all__ = ['BookSearchFilter']

from typing import TypedDict

class BookSearchFilter(TypedDict):
	owner: str|None
	title: str|None
	author: str|None
	genre: str|None
	shared: bool|None