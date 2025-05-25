"""application.types.schemareturntype"""

from typing import TypedDict


class SchemaReturnType(TypedDict):
	type: str
	optional: bool
	array: bool
