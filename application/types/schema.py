from typing import TypedDict
from .schemaquery import SchemaQuery
from .schematype import SchemaType

class Schema(TypedDict):
	mutations: list[SchemaQuery | None]
	queries: list[SchemaQuery | None]
	types: list[SchemaType | None]

