from typing import TypedDict


class InvalidFields(TypedDict):
	message: str
	fields: list[str]
