from typing import TypedDict
from .schemaparam import SchemaParam


class SchemaType(TypedDict):
	type: str
	union: bool
	subtypes: list[str]
	params: list[SchemaParam | None]
