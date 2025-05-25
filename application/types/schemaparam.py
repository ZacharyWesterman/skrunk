"""application.types.schemaparam"""

from typing import TypedDict


class SchemaParam(TypedDict):
	"""
	A parameter in a GraphQL schema query.
	"""

	## The name of the parameter.
	name: str
	## The type of the parameter.
	type: str
	## Whether the parameter is optional.
	optional: bool
