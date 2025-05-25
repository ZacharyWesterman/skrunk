"""application.types.book"""

from typing import TypedDict
from datetime import datetime
from .bookident import BookIdent
from .usermindata import UserMinData
from .bookshare import BookShare
from .bookownerhist import BookOwnerHist
from .ebook import EBook


class Book(TypedDict):
	id: str
	title: str
	subtitle: str | None
	authors: list[str]
	publisher: str
	publishedDate: datetime
	has_description: bool
	industryIdentifiers: list[BookIdent]
	pageCount: int
	categories: list[str]
	maturityRating: str
	language: str
	thumbnail: str | None
	smallThumbnail: str | None
	creator: str
	owner: UserMinData
	shared: bool
	shareHistory: list[BookShare]
	rfid: str
	ownerHistory: list[BookOwnerHist]
	ebooks: list[EBook]
	audiobook: str | None
