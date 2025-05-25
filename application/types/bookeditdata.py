from typing import TypedDict


class BookEditData(TypedDict):
	title: str
	subtitle: str | None
	authors: list[str]
