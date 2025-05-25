"""application.types.schematype"""

from typing import TypedDict
from .schemaparam import SchemaParam


class SchemaType(TypedDict):
	"""
	A type in the GraphQL schema.
	"""

	## The name of the type.
	type: str
	## Whether the type is a union type.
	union: bool
	## If the type is a union, the subtypes it can be.
	subtypes: list[str]
	## If the type is non-scalar, the list of child parameters.
	params: list[SchemaParam]
