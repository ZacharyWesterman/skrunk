"""application.types.inventorysearchfilter"""

from typing import TypedDict


class InventorySearchFilter(TypedDict):
	owner: str | None
	category: str | None
	type: str | None
	location: str | None
