from typing import TypedDict


class InventorySearchFilter(TypedDict):
	owner: str
	category: str
	type: str
	location: str
