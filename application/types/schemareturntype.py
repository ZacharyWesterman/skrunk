"""application.types.schemareturntype"""

from typing import TypedDict
from bson.objectid import ObjectId


class SchemaReturnType(TypedDict):
	"""
	A return type in a GraphQL schema query.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The type of the return value.
	type: str
	## Whether the return value is nullable.
	optional: bool
	## Whether the return value is an array.
	array: bool
