from application.db.inventory import *
import application.db.perms as perms
from application.db.users import group_filter

def resolve_get_item_categories(_, info) -> list[str]:
	return get_item_categories()

def resolve_get_item_types(_, info, category: str) -> list[str]:
	return get_item_types(category)

def resolve_get_item_locations(_, info, owner: str) -> list[str]:
	return get_item_locations(owner)
