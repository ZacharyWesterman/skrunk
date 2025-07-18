"""application.types.schema"""

from typing import TypedDict
from bson.objectid import ObjectId
from .schemaquery import SchemaQuery
from .schematype import SchemaType


class Schema(TypedDict):
	"""
	A type representing the complete GraphQL schema.
	"""

	## The unique identifier of the document.
	_id: ObjectId
	## A list of all mutations in the schema.
	mutations: list[SchemaQuery]
	## A list of all queries in the schema.
	queries: list[SchemaQuery]
	## A list of all types in the schema.
	types: list[SchemaType]
