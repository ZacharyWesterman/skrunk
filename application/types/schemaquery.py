"""application.types.schemaquery"""

from typing import TypedDict
from bson.objectid import ObjectId
from .schemaparam import SchemaParam
from .schemareturntype import SchemaReturnType


class SchemaQuery(TypedDict):
	"""
	A query in the GraphQL schema.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## The name of the query.
	name: str
	## A list of parameters for the query.
	params: list[SchemaParam]
	## A text representation of the query.
	query: str
	## The return type of the query.
	returns: SchemaReturnType
