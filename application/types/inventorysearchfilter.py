"""application.types.inventorysearchfilter"""

from typing import TypedDict


class InventorySearchFilter(TypedDict):
	"""
	An input type for filtering inventory items.
	All fields are optional, and if a field is null, it will not be used in the query.
	"""

	## The username of the owner of the item.
	owner: str | None
	## The category of the item, such as 'electronics', 'furniture', etc.
	category: str | None
	## The type of the item, such as 'laptop', 'chair', etc.
	type: str | None
	## The location where the item is stored, such as 'office', 'warehouse', etc.
	location: str | None
