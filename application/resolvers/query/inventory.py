"""application.resolvers.query.inventory"""

from graphql.type import GraphQLResolveInfo

from application.db import perms
from application.db.inventory import (count_inventory, get_inventory,
                                      get_item_categories, get_item_locations,
                                      get_item_types)
from application.db.users import group_filter
from application.objects import InventorySearchFilter, Sorting

from . import query


@query.field('getItemCategories')
@perms.module('inventory')
def resolve_get_item_categories(_, _info: GraphQLResolveInfo) -> list[str]:
	return get_item_categories()


@query.field('getItemTypes')
@perms.module('inventory')
def resolve_get_item_types(_, _info: GraphQLResolveInfo, category: str) -> list[str]:
	return get_item_types(category)


@query.field('getItemLocations')
@perms.module('inventory')
def resolve_get_item_locations(_, _info: GraphQLResolveInfo, owner: str) -> list[str]:
	return get_item_locations(owner)


@query.field('getInventory')
@perms.module('inventory')
def resolve_get_inventory(_, _info: GraphQLResolveInfo, filter: InventorySearchFilter, start: int, count: int, sorting: Sorting) -> list[dict]:
	user_data = perms.caller_info_strict()
	return get_inventory(group_filter(filter, user_data), start, count, sorting)


@query.field('countInventory')
@perms.module('inventory')
def resolve_count_inventory(_, _info: GraphQLResolveInfo, filter: InventorySearchFilter) -> int:
	user_data = perms.caller_info_strict()
	return count_inventory(group_filter(filter, user_data))
