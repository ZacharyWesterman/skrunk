"""application.types.invalidfields"""

from typing import TypedDict


class InvalidFields(TypedDict):
	"""
	An error indicating that certain fields in the request are invalid.
	"""

	## A message describing the error.
	message: str
	## A list of fields that are invalid.
	fields: list[str]
