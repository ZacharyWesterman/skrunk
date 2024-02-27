from application.db.inventory import *
import application.db.perms as perms
from application.db.users import group_filter
from application.objects import InventorySearchFilter, Sorting

def resolve_get_item_categories(_, info) -> list[str]:
	return get_item_categories()

def resolve_get_item_types(_, info, category: str) -> list[str]:
	return get_item_types(category)

def resolve_get_item_locations(_, info, owner: str|None) -> list[str]:
	return get_item_locations(owner)

def resolve_get_inventory(_, info, filter: InventorySearchFilter, start: int, count: int, sorting: Sorting) -> list:
	user_data = perms.caller_info()
	return get_inventory(group_filter(filter, user_data), start, count, sorting, user_data['_id'])

def resolve_count_inventory(_, info, filter: InventorySearchFilter) -> int:
	user_data = perms.caller_info()
	print(filter, flush=True)
	return count_inventory(group_filter(filter, user_data), user_data['_id'])
