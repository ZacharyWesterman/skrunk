from typing import TypedDict

class BookEditData(TypedDict):
	title: str
	subtitle: str
	authors: list[str]

