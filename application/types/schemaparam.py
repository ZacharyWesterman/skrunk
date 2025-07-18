"""application.types.schemaparam"""

from typing import TypedDict
from bson.objectid import ObjectId


class SchemaParam(TypedDict):
	"""
	A parameter in a GraphQL schema query.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The name of the parameter.
	name: str
	## The type of the parameter.
	type: str
	## Whether the parameter is optional.
	optional: bool
