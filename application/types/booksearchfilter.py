from typing import TypedDict


class BookSearchFilter(TypedDict):
	owner: str
	title: str
	author: str
	genre: str
	shared: bool
