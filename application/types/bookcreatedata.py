"""application.types.bookcreatedata"""

from typing import TypedDict
from datetime import datetime


class BookCreateData(TypedDict):
	"""
	Data for creating a new book entry.
	"""

	## The title of the book.
	title: str
	## The subtitle of the book, if any.
	subtitle: str | None
	## The book authors.
	authors: list[str]
	## The description of the book.
	description: str | None
	## The page count of the book.
	pageCount: int
	## An industry identifier for the book, such as ISBN.
	isbn: str
	## The publisher of the book.
	publisher: str
	## The date the book was published.
	publishedDate: datetime
	## The RFID tag or QR code associated with the book.
	rfid: str
	## The thumbnail image URL for the book cover, if any.
	thumbnail: str | None
