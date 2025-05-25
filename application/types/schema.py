from typing import TypedDict
from .schemaquery import SchemaQuery
from .schematype import SchemaType


class Schema(TypedDict):
	mutations: list[SchemaQuery]
	queries: list[SchemaQuery]
	types: list[SchemaType]
