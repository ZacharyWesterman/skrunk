"""application.types.bookident"""

from typing import TypedDict


class BookIdent(TypedDict):
	type: str
	identifier: str
