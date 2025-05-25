"""application.types.sorting"""

from typing import TypedDict


class Sorting(TypedDict):
	fields: list[str]
	descending: bool
