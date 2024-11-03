import application.db.perms as perms
from application.db.inventory import create_inventory_item, get_inventory_item, delete_inventory_item
from ..decorators import *
from . import mutation

@mutation.field('createInventoryItem')
@perms.module('inventory')
@perms.require('edit')
@handle_client_exceptions
def resolve_create_inventory_item(_, info, owner: str, category: str, type: str, location: str, blob_id: str, description: str, rfid: str|None) -> dict:
	if category.strip() == '' or type.strip() == '' or location.strip() == '' or blob_id.strip() == '':
		fields = []
		if category.strip() == '': fields += ['category']
		if type.strip() == '': fields += ['type']
		if location.strip() == '': fields += ['location']
		if blob_id.strip() == '': fields += ['blob_id']

		return {
			'__typename': 'InvalidFields',
			'message': f'The following field{"" if len(fields) == 1 else "s"} cannot be blank',
			'fields': fields,
		}

	return { '__typename': 'Item', **create_inventory_item(owner, category, type, location, blob_id, description, rfid) }

@mutation.field('deleteInventoryItem')
@perms.module('inventory')
@perms.require('edit')
@perms.require('admin', perform_on_self = True, data_func = get_inventory_item)
@handle_client_exceptions
def resolve_delete_inventory_item(_, info, id: str) -> dict:
	return { '__typename': 'Item', **delete_inventory_item(id) }
