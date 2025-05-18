"""application.objects"""

from typing import TypedDict
from datetime import datetime


class BookSearchFilter(TypedDict):
	"""
	A TypedDict for filtering book search results.

	Attributes:
		owner (str | None): The owner of the book.
		title (str | None): The title of the book.
		author (str | None): The author of the book.
		genre (str | None): The genre of the book.
		shared (bool | None): Indicates if the book is shared.
	"""
	## The owner of the book.
	owner: str | None
	## The title of the book.
	title: str | None
	## The author of the book.
	author: str | None
	## The genre of the book.
	genre: str | None
	## Indicates if the book is shared.
	shared: bool | None


class BlobSearchFilter(TypedDict):
	"""
	BlobSearchFilter is a TypedDict that defines the structure for filtering blob search results.

	Attributes:
		creator (str | None): The creator of the blob. Can be None if not specified.
		begin_date (datetime | None): The start date for the search filter. Can be None if not specified.
		end_date (datetime | None): The end date for the search filter. Can be None if not specified.
		name (str | None): The name of the blob. Can be None if not specified.
		tag_expr (str | None): The tag expression for filtering blobs. Can be None if not specified.
	"""
	## The creator(s) of the blob.
	creator: list[str] | str | None
	## The start date for the search filter.
	begin_date: datetime | None
	## The end date for the search filter.
	end_date: datetime | None
	## The name of the blob.
	name: str | None
	## The tag expression for filtering blobs.
	tag_expr: str | None


class Sorting(TypedDict):
	"""
	A TypedDict representing sorting options for a collection of items.

	Attributes:
		fields (list[str]): A list of field names to sort by.
		descending (bool): A boolean indicating if the sorting should be in descending order.
	"""
	## A list of field names to sort by.
	fields: list[str]
	## A boolean indicating if the sorting should be in descending order.
	descending: bool


class InventorySearchFilter(TypedDict):
	"""
	A TypedDict for filtering inventory search results.

	Attributes:
		creator (str | None): The creator of the inventory item.
		category (str | None): The category of the inventory item.
		type (str | None): The type of the inventory item.
		location (str | None): The location of the inventory item.
	"""
	## The creator(s) of the inventory item
	creator: list[str] | str | None
	## The category of the inventory item
	category: str | None
	## The type of the inventory item
	type: str | None
	## The location of the inventory item
	location: str | None
