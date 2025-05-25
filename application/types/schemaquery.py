from typing import TypedDict
from .schemaparam import SchemaParam
from .schemareturntype import SchemaReturnType


class SchemaQuery(TypedDict):
	name: str
	params: list[SchemaParam]
	query: str
	returns: SchemaReturnType
