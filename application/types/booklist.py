"""application.types.booklist"""

from typing import TypedDict
from .book import Book


class BookList(TypedDict):
	books: list[Book]
