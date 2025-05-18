from typing import TypedDict
from .schemaparam import SchemaParam
from .schemareturntype import SchemaReturnType

class SchemaQuery(TypedDict):
	name: str
	params: list[SchemaParam | None]
	query: str
	returns: SchemaReturnType | None

