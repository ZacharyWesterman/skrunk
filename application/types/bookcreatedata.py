from typing import TypedDict
from datetime import datetime


class BookCreateData(TypedDict):
	title: str
	subtitle: str | None
	authors: list[str]
	description: str | None
	pageCount: int
	isbn: str
	publisher: str
	publishedDate: datetime
	rfid: str
	thumbnail: str | None
