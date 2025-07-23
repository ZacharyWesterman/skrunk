"""application.resolvers.query.inventory"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.inventory import (count_inventory, get_inventory,
                                      get_item_categories, get_item_locations,
                                      get_item_types)
from application.db.users import group_filter
from application.types import InventorySearchFilter, Sorting

from . import query


@query.field('getItemCategories')
@perms.module('inventory')
def resolve_get_item_categories(_, _info: GraphQLResolveInfo) -> list[str]:
	"""
	Retrieves a list of item categories.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.

	Returns:
		list[str]: A list of item category names as strings.
	"""
	return get_item_categories()


@query.field('getItemTypes')
@perms.module('inventory')
def resolve_get_item_types(_, _info: GraphQLResolveInfo, category: str) -> list[str]:
	"""
	Retrieves a list of item types for a given category.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		category (str): The category for which to fetch item types.

	Returns:
		list[str]: A list of item type strings associated with the specified category.
	"""
	return get_item_types(category)


@query.field('getItemLocations')
@perms.module('inventory')
def resolve_get_item_locations(_, _info: GraphQLResolveInfo, owner: str) -> list[str]:
	"""
	Retrieves the locations of items owned by a specified owner.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		owner (str): The identifier of the owner whose item locations are to be retrieved.

	Returns:
		list[str]: A list of locations (as strings) where the owner's items are stored.
	"""
	return get_item_locations(owner)


@query.field('getInventory')
@perms.module('inventory')
def resolve_get_inventory(_, _info: GraphQLResolveInfo, filter: InventorySearchFilter, start: int, count: int, sorting: Sorting) -> list[dict]:
	"""
	Retrieves a list of inventory items based on the provided filter, pagination, and sorting options.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		filter (InventorySearchFilter): Criteria to filter inventory items.
		start (int): The starting index for pagination.
		count (int): The number of items to retrieve.
		sorting (Sorting): Sorting options for the inventory list.

	Returns:
		list[dict]: A list of inventory items matching the filter and sorting criteria.
	"""
	user_data = perms.caller_info_strict()
	return get_inventory(
		group_filter(filter, user_data),  # type: ignore[arg-type]
		start,
		count,
		sorting
	)


@query.field('countInventory')
@perms.module('inventory')
def resolve_count_inventory(_, _info: GraphQLResolveInfo, filter: InventorySearchFilter) -> int:
	"""
	Resolves the count of inventory items based on the provided search filter.

	Args:
		_ (Any): Placeholder.
		_info (GraphQLResolveInfo): Information about the GraphQL execution state.
		filter (InventorySearchFilter): Filter criteria for searching inventory items.

	Returns:
		int: The number of inventory items matching the filter and user permissions.
	"""
	user_data = perms.caller_info_strict()
	return count_inventory(
		group_filter(filter, user_data)  # type: ignore[arg-type]
	)
