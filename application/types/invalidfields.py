"""application.types.invalidfields"""

from typing import TypedDict
from bson.objectid import ObjectId


class InvalidFields(TypedDict):
	"""
	An error indicating that certain fields in the request are invalid.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## A message describing the error.
	message: str
	## A list of fields that are invalid.
	fields: list[str]
