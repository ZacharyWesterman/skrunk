from application.db.inventory import *
import application.db.perms as perms
from application.db.users import group_filter
from application.objects import InventorySearchFilter, Sorting
from . import query

@query.field('getItemCategories')
@perms.module('inventory')
def resolve_get_item_categories(_, info) -> list[str]:
	return get_item_categories()

@query.field('getItemTypes')
@perms.module('inventory')
def resolve_get_item_types(_, info, category: str) -> list[str]:
	return get_item_types(category)

@query.field('getItemLocations')
@perms.module('inventory')
def resolve_get_item_locations(_, info, owner: str|None) -> list[str]:
	return get_item_locations(owner)

@query.field('getInventory')
@perms.module('inventory')
def resolve_get_inventory(_, info, filter: InventorySearchFilter, start: int, count: int, sorting: Sorting) -> list:
	user_data = perms.caller_info()
	return get_inventory(group_filter(filter, user_data), start, count, sorting, user_data['_id'])

@query.field('countInventory')
@perms.module('inventory')
def resolve_count_inventory(_, info, filter: InventorySearchFilter) -> int:
	user_data = perms.caller_info()
	return count_inventory(group_filter(filter, user_data), user_data['_id'])
