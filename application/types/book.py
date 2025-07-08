"""application.types.book"""

from typing import TypedDict
from datetime import datetime
from .bookident import BookIdent
from .usermindata import UserMinData
from .bookshare import BookShare
from .bookownerhist import BookOwnerHist
from .ebook import EBook


class Book(TypedDict):
	"""
	A type for information about a linked book.
	"""

	## The unique identifier for the book.
	id: str
	## The title of the book.
	title: str
	## The subtitle of the book, if any.
	subtitle: str | None
	## The authors of the book.
	authors: list[str]
	## The publisher of the book.
	publisher: str
	## The date the book was published.
	publishedDate: datetime
	## Whether the book has a description. If true, the description can be fetched using the getBookDescription query, but by default it is not included in the book data, to save bandwidth.
	has_description: bool
	## The description of the book, if available.
	description: str | None
	## A list of industry identifiers for the book, such as ISBN.
	industryIdentifiers: list[BookIdent]
	## The page count of the book.
	pageCount: int
	## A list of categories the book belongs to, such as fiction, non-fiction, etc.
	categories: list[str]
	## The maturity rating of the book, such as 'MATURE', 'NOT_MATURE', etc.
	maturityRating: str
	## The language the book is written in, e.g., 'en' for English.
	language: str
	## The URL to the book's cover image, if any.
	thumbnail: str | None
	## The URL to a smaller version of the book's cover image, if any.
	smallThumbnail: str | None
	## The ID of the user who created the book entry.
	creator: str
	## Minimal user data for the owner of the book.
	owner: UserMinData
	## Whether the book is shared with someone other than the owner.
	shared: bool
	## The history of sharing the book with other users.
	shareHistory: list[BookShare]
	## The RFID tag or QR code associated with the book.
	rfid: str
	## The history of ownership changes for the book.
	ownerHistory: list[BookOwnerHist]
	## A list of any eBooks associated with the book.
	ebooks: list[EBook]
	## The ID of the audiobook associated with the book, if any.
	audiobook: str | None
