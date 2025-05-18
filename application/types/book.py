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
	subtitle: str
	authors: list[str]
	publisher: str
	publishedDate: datetime
	has_description: bool
	industryIdentifiers: list[BookIdent | None]
	pageCount: int
	categories: list[str]
	maturityRating: str
	language: str
	thumbnail: str
	smallThumbnail: str
	creator: str
	owner: UserMinData | None
	shared: bool
	shareHistory: list[BookShare | None]
	rfid: str
	ownerHistory: list[BookOwnerHist | None]
	ebooks: list[EBook | None]
	audiobook: str
